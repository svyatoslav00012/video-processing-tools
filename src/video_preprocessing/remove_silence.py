import os
import subprocess
from enum import Enum

from src.video_preprocessing.tools import add_name_postfix, extract_rotation_degree

def main():
    video_path = 'replace_with_your_video_path'
    remove_silence(video_path)
    # print(AutoEditExportOptions.SHOTCUT.val())

# class AutoEditExportOptions(Enum):
#     DEFAULT = "default",
#     PREMIERE = "premiere",
#     RESOLVE = "resolve",
#     FINAL_CUT_PRO = "final_cut_pro",
#     SHOTCUT = "shotcut",
#     JSON = "json",
#     TIMELINE = "timeline",
#     AUDIO = "audio"
#
#     def val(self):
#         return self.value[0]
#
#


def remove_silence(video_path: str, margin_before: float = 0.3, margin_after: float = 1.0) -> str:
    output_path = add_name_postfix(video_path, 'no_silence')
    command = f"auto-editor {video_path} --margin {margin_before}s,{margin_after}sec --debug --no-open --output {output_path}"
    subprocess.call(command, shell=True)

    initial_rotation_degree = extract_rotation_degree(video_path)

    # if abs(initial_rotation_degree) < 1:
    #     transpose_param = get_transpose_param(-initial_rotation_degree)
    #     print('rotating...')
    #     rotated_path = add_name_postfix(output_path, 'rotated')
    #     rotate_video_command = f"ffmpeg -i {output_path} -vf {transpose_param} -c:a copy {rotated_path}"
    #     subprocess.call(rotate_video_command, shell=True)
    #     os.remove(output_path)
    #     os.rename(rotated_path, output_path)

    return output_path

def get_transpose_param(rotation_degree: int) -> str:
    if rotation_degree == 90:
        return 'transpose=1'
    elif rotation_degree == 180 or rotation_degree == -180:
        return 'transpose=1,transpose=1'
    elif rotation_degree == 270 or rotation_degree == -90:
        return 'transpose=2'
    else:
        return ''

main()
