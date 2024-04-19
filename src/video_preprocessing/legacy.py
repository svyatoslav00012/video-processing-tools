def align_audio_ffmpeg(video_path, audio_path, output_path):
    # Get the delay between the video and the audio
    delay_seconds = extract_audio_delay(video_path, audio_path)
    if delay_seconds > 0:
        command = 'ffmpeg -i audio.aiff -af "adelay=delay_seconds|delay_seconds" delayed_audio.aiff'


def align_audio(video_path, audio_path, output_path):
    delay_seconds = extract_audio_delay(video_path, audio_path)

    # Adjust the new audio signal by the delay
    if delay_seconds > 0:
        print("Trimming new audio (delay positive)...")
        new_audio = new_audio.subclip(delay_seconds, new_audio.duration)
    else:
        print("Adjusting start of new audio (delay negative)...")
        new_audio = new_audio.set_start(-delay_seconds)

    # Set the audio of the video clip to the new audio
    print("Setting the audio of the video clip to the new synchronized audio...")
    video = video.set_audio(new_audio)

    # Write the result to a file
    print("Writing the result to a file...")
    video.write_videofile(output_path, codec='libx264', audio_codec='aac')

def extract_audio_delay_legacy(video_path, audio_path):
    print('Loading video...')
    video_audio = AudioFileClip(video_path)

    # Load the external AIFF audio
    print('Loading audio...')
    new_audio = AudioFileClip(audio_path)

    # Convert audio signals to numpy arrays
    print("Converting original video's audio signals to numpy arrays...")
    video_audio_signal = video_audio.audio.to_soundarray(fps=44100)
    print("Converting new audio's signals to numpy arrays...")
    new_audio_signal = new_audio.to_soundarray(fps=44100)

    # Compute cross-correlation
    print("Computing cross-correlation...")
    correlation = correlate(video_audio_signal.flatten(), new_audio_signal.flatten(), mode='full')
    delay_index = correlation.argmax()
    print(correlation)
    print("Computed delay index (argmax of correlation):", delay_index)

    # Calculate delay in samples
    computed_delay = delay_index - (len(new_audio_signal) - 1)
    print("Computed delay in samples:", computed_delay)

    # Convert delay from samples to seconds
    delay_seconds = computed_delay / 44100
    print("Computed delay in seconds:", delay_seconds)
