import subprocess

from src.video_preprocessing.tools import add_name_postfix


def adjust_volume(video_path: str, db_change: float) -> str:
    output_path = add_name_postfix(video_path, f'volume_{db_change}db')
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-af', f'volume={db_change}dB',
        '-c:v', 'copy',  # Copy the video stream without re-encoding
        '-c:a', 'aac',  # Re-encode audio to maintain compatibility if necessary
        output_path
    ]
    subprocess.call(cmd)
    return output_path
