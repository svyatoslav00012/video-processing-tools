import io
import os
from os import system
from threading import Thread
from time import sleep
import time
from typing import Iterable

import dotenv
import torch
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment, TranscriptionInfo
from tqdm import tqdm


def main():
    your_video_file = ''
    faster_whisper_transcribe(your_video_file)


dotenv.load_dotenv()

model_size = os.getenv("WHISPER_MODEL_SIZE")

GPU_COMPUTE_TYPE = os.getenv("WHISPER_GPU_COMPUTE_TYPE")
CPU_COMPUTE_TYPE = os.getenv("WHISPER_CPU_COMPUTE_TYPE")

CPU_BEAM_SIZE = int(os.getenv("WHISPER_CPU_BEAM_SIZE"))
GPU_BEAM_SIZE = int(os.getenv("WHISPER_GPU_BEAM_SIZE"))


def preload_model(model_size: str):
    device = select_device(is_mps_supported=False)
    compute_type = select_compute_type(device)
    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type
    )
    return model


def select_device(is_mps_supported=True):
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available() and is_mps_supported:
        return "mps"
    else:
        return "cpu"


def select_compute_type(device):
    if device == "cuda" or device == "mps":
        return GPU_COMPUTE_TYPE
    else:
        return CPU_COMPUTE_TYPE


def find_out_beam_size(model: WhisperModel) -> int:
    if model.model.device == "cuda":
        return GPU_BEAM_SIZE
    else:
        return CPU_BEAM_SIZE


model = preload_model(model_size)
beam_size = find_out_beam_size(model)

def faster_whisper_transcribe(file_path: str) -> list[Segment]:
    segments_generator, info = model.transcribe(
        file_path,
        beam_size=beam_size,
        language="en",
        word_timestamps=True,
        # vad_filter=True,
        # vad_parameters=dict(min_silence_duration_ms=500)
    )
    # return [s for s in segments]
    return transcribe_while_printing_progress(segments_generator, info)




def transcribe_while_printing_progress(segments_generator: Iterable[Segment], info: TranscriptionInfo) -> list[Segment]:
    def pbar_delayed():  # to get last timestamp from chunk
        global timestamp_prev
        sleep(set_delay)  # wait for whole chunk to be iterated
        pbar.update(timestamp_last - timestamp_prev)
        timestamp_prev = timestamp_last
        # system("title " + capture.getvalue().splitlines()[-1].replace("|", "^|").replace("<", "^<").replace("?", "0"))
        print(capture.getvalue().splitlines()[-1])

    total_dur = round(info.duration)
    td_len = str(len(str(total_dur)))  # get length for n_fmt
    global timestamp_prev, timestamp_last
    timestamp_prev = 0  # last timestamp in previous chunk
    timestamp_last = 0  # current timestamp
    capture = io.StringIO()  # capture progress bars from tqdm
    last_burst = 0.0  # time of last iteration burst aka chunk
    set_delay = 0.1  # max time it takes to iterate chunk & minimum time between chunks.

    s_time = time.time()
    print("")
    bar_f = "{percentage:3.0f}% | {n_fmt:>" + td_len + "}/{total_fmt} | {elapsed}<<{remaining} | {rate_noinv_fmt}"

    result: list[Segment] = []

    with tqdm(file=capture, total=total_dur, unit=" audio seconds", smoothing=0.00001, bar_format=bar_f) as pbar:
        for segment in segments_generator:
            result.append(segment)
            # print(segment)
            # for word in segment.words:
            #     print(word)
            timestamp_last = round(segment.end)
            time_now = time.time()
            if time_now - last_burst > set_delay:  # catch new chunk
                last_burst = time_now
                Thread(target=pbar_delayed, daemon=False).start()
        sleep(set_delay + 0.3)  # wait for the last pbar_delayed to finish
        if timestamp_last < total_dur:  # silence at the end of the audio
            pbar.update(total_dur - timestamp_last)
            print(capture.getvalue().splitlines()[-1])

    print("\n\nFinished! Speed: %s audio seconds/s" % round(info.duration / ((time.time() - s_time)), 2))

    return result

main()