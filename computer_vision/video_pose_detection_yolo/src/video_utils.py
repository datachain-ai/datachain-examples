import io
import os
import sys

import imageio
import shutil

from datachain import File


def open_video(file: File):
    return imageio.get_reader(io.BytesIO(file.read()), format=file.get_file_ext())


def split_video_to_frames(
    file: File,
    output_dir: str,
    step: int = 1,
    rewrite: bool = True
) -> None:
    """
    Split a video into frames and save them as images.

    Args:
        file (File): DataChain file object.
        output_dir (str): Directory to save the output frames.
        step (int, optional): Step size for frame extraction. Defaults to 1.
        rewrite (bool, optional): Whether to overwrite existing output directory. Defaults to True.

    Raises:
        SystemExit: If the video file cannot be opened or if the step size is invalid.
    """
    dir_name = os.path.dirname(file.get_full_name())
    file_name = os.path.basename(file.get_full_name())
    video_id = file_name[:11]
    frames_output_dir = os.path.join(output_dir, dir_name, video_id)

    if os.path.exists(frames_output_dir):
        if rewrite:
            shutil.rmtree(frames_output_dir)
        else:
            print(f"Subdirectory already exists: {frames_output_dir}")
            sys.exit(1)

    os.makedirs(frames_output_dir)

    if not isinstance(step, int) or step <= 0:
        print("Error: Step must be an integer greater than 0.")
        sys.exit(1)

    reader = open_video(file)
    saved_frames = 0
    for frame, img in enumerate(reader):
        if frame % step:
            continue
        imageio.imwrite(os.path.join(frames_output_dir, f"{frame:04d}.jpg"), img)
        saved_frames += 1

    print(f"Saved {saved_frames} frames from {file_name} to {frames_output_dir}")
