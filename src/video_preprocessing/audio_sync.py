import json
import os
import subprocess
import time

import librosa
from scipy.signal import correlate

from src.video_preprocessing.tools import remove_if_exists

VIDEO_1_PATH = 'video/place_your_video_here.mp4'
AUDIO_1_PATH = 'video/place_your_audio_here.wav'
OUTPUT_1_PATH = 'video/1_audio_swapped.mp4'

def main():
    time_now = time.time()
    swap_audio_in_video(VIDEO_1_PATH, AUDIO_1_PATH, OUTPUT_1_PATH)
    print('done in', time.time() - time_now)


def swap_audio_in_video(video_path, mic_audio_path, output_path):
    delay_seconds = extract_audio_delay(video_path, mic_audio_path)
    wav_path = convert_mic_audio_to_wav(mic_audio_path)
    audio_with_delay_path = apply_audio_delay(wav_path, delay_seconds)
    replace_audio(video_path, audio_with_delay_path, output_path)


def extract_audio_delay(video_path: str, audio_path: str) -> float:
    print('extracting audio from video...')
    audio_info = get_media_info(audio_path)
    print(json.dumps(audio_info, indent=4))
    audio_sample_rate = int(audio_info['streams'][0]['sample_rate'] or 48000)
    audio_channels = 1 if audio_info['streams'][0]['channel_layout'] == 'mono' else 2

    video_audio_path = 'video/temp/video_audio.wav'
    remove_if_exists(video_audio_path)
    command = f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar {audio_sample_rate} -ac {audio_channels} {video_audio_path}"
    subprocess.call(command, shell=True)

    print('loading audio...')
    # Load the WAV audio extracted from the video
    video_audio, sr_video = librosa.load(video_audio_path, sr=None, mono=True)

    # Load the AIFF audio file
    mic_audio, sr_mic = librosa.load(audio_path, sr=None, mono=True)

    # Compute cross-correlation
    print("Computing cross-correlation...")
    xcorr = correlate(video_audio, mic_audio, mode='full')

    # Calculate delay
    delay_samples = xcorr.argmax() - len(mic_audio)
    delay_seconds = delay_samples / float(sr_video)

    print(f"Delay: {delay_seconds} seconds")
    return delay_seconds


def convert_mic_audio_to_wav(audio_path: str) -> str:
    # Step 1: Convert AIFF to WAV (if needed)
    extension = audio_path.split('.')[-1]
    wav_audio_path = audio_path
    if audio_path.endswith(extension) and extension != 'wav':
        wav_audio_path = audio_path.replace('video', 'video/temp').replace('.' + extension, '.wav')
        remove_if_exists(wav_audio_path)
        print("Converting AIFF to WAV...")
        subprocess.call(f'ffmpeg -i "{audio_path}" "{wav_audio_path}"', shell=True)
    return wav_audio_path


def apply_audio_delay(wav_audio_path: str, delay_seconds: float) -> str:
    # Step 2: Apply delay
    audio_with_delay_path = wav_audio_path.replace('.wav', '_adjusted.wav')

    if delay_seconds > 0:
        print("Applying positive delay...")
        remove_if_exists(audio_with_delay_path)
        subprocess.call(
            f'ffmpeg -i "{wav_audio_path}" -af "adelay={int(delay_seconds * 1000)}|{int(delay_seconds * 1000)}" "{audio_with_delay_path}"',
            shell=True)
    elif delay_seconds < 0:
        print("Applying negative delay...")
        trim_start = abs(delay_seconds)
        remove_if_exists(audio_with_delay_path)
        subprocess.call(f'ffmpeg -i "{wav_audio_path}" -ss {trim_start} "{audio_with_delay_path}"',
                        shell=True)
    else:
        audio_with_delay_path = wav_audio_path
    return audio_with_delay_path


def replace_audio(video_path: str, audio_path: str, output_path: str):
    # Step 3: Replace audio in video
    print("Replacing audio in video...")
    remove_if_exists(output_path)
    subprocess.call(
        f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -map 0:v:0 -map 1:a:0 "{output_path}"',
        shell=True)

    print("Replacement complete, file saved to:", output_path)


main()
