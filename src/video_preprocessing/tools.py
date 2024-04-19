import json
import os
import subprocess


def add_name_postfix(path_name: str, postfix: str) -> str:
    extension = path_name.split('.')[-1]
    return path_name.replace('.' + extension, f'_{postfix}.{extension}')


def remove_if_exists(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def generate_test_bad_audio(src_audio_path, dest_audio_path):
    command = f'ffmpeg -i {src_audio_path} -ar 22050 -acodec libmp3lame {dest_audio_path}'
    print(subprocess.call(command, shell=True))


def print_media_info(media_path):
    media_info = get_media_info(media_path)
    # media_info = get_media_info_1(media_path)
    print(json.dumps(media_info, indent=4))


def extract_rotation_degree(video_path):
    media_info = get_media_info(video_path)
    streams = media_info.get('streams', [{}])
    video_stream = next((stream for stream in streams if stream.get('codec_type') == 'video'), {})
    side_data_list = video_stream.get('side_data_list', [])
    display_matrix_side_data = next(
        (side_data for side_data in side_data_list if side_data.get('side_data_type') == 'Display Matrix'), {})
    rotation = display_matrix_side_data.get('rotation', 0)
    return rotation

# Exmple output:
#{
#     "programs": [],
#     "streams": [
#         {
#             "codec_name": "aac",
#             "codec_type": "audio",
#             "sample_rate": "48000",
#             "channel_layout": "stereo",
#             "r_frame_rate": "0/0",
#             "tags": {}
#         },
#         {
#             "codec_name": "h264",
#             "codec_type": "video",
#             "width": 1080,
#             "height": 1920,
#             "r_frame_rate": "30/1",
#             "tags": {},
#             "side_data_list": [
#                 {
#                     "side_data_type": "Display Matrix",
#                     "displaymatrix": "\n00000000:            0      -65536           0\n00000001:        65536           0           0\n00000002:            0           0  1073741824\n",
#                     "rotation": 90
#                 }
#             ]
#         }
#     ],
#     "format": {
#         "duration": "222.365875",
#         "size": "286288241",
#         "bit_rate": "10299718"
#     }
# }
def get_media_info(media_path) -> dict:
    """Get detailed media information using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=duration,bit_rate,size:stream=codec_type,codec_name,width,height,r_frame_rate,channel_layout,sample_rate:stream_tags=rotate:stream_side_data_list",
        "-of", "json",
        media_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return json.loads(result.stdout)