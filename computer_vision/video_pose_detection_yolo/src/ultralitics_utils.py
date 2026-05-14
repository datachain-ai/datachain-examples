import numpy as np
import torch
from PIL import Image

from ultralytics.engine.results import Boxes, Keypoints, Results


def process_annotation(pose_annotation) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Process a single pose annotation.

    Args:
        pose_annotation: Pose annotation object.

    Returns:
        tuple[torch.Tensor, torch.Tensor]: Processed boxes and keypoints data.
    """
    data = pose_annotation.model_dump()

    boxes = torch.tensor([[*data['box']['coords'], data['confidence'], data['cls']]])

    keypoints = torch.tensor([
        list(zip(
            data['pose']['x'],
            data['pose']['y'],
            data['pose']['visible']
        ))
    ])
    # keypoints = keypoints.unsqueeze(0)  # Add batch dimension: Shape: (1, 17, 3)

    return boxes, keypoints


def extract_yolo_results(detections: list, orig_shape: tuple) -> tuple[Boxes, Keypoints]:
    """
    Extract YOLO results from a list of detections.

    Args:
        detections (list): list of detection objects.
        orig_shape (tuple): Original shape of the image.

    Returns:
        tuple[Boxes, Keypoints]: Processed boxes and keypoints.
    """
    all_boxes_data = []
    all_keypoints_data = []

    for pose in detections:
        boxes, keypoints = process_annotation(pose)
        all_boxes_data.append(boxes)
        all_keypoints_data.append(keypoints)

    if all_boxes_data:
        all_boxes_data = torch.cat(all_boxes_data, dim=0)
    if all_keypoints_data:
        all_keypoints_data = torch.cat(all_keypoints_data, dim=0)

    boxes = Boxes(all_boxes_data, orig_shape)
    keypoints = Keypoints(all_keypoints_data, orig_shape)

    return boxes, keypoints


def visualize_ultralytics_results(results: Results, scale: float = 1.0) -> Image.Image:
    """
    Visualize Ultralytics Results object.

    Args:
        results (Results): Results object from Ultralytics model.
        scale (float): Scale factor for resizing the image. Default is 1.0.

    Returns:
        Image.Image: Visualized and resized image.
    """
    im_bgr = results.plot(
        font_size=20,
        kpt_radius=5,
    )

    im_rgb = Image.fromarray(im_bgr[..., ::-1])

    orig_height, orig_width = results.orig_shape
    new_size = (int(orig_width * scale), int(orig_height * scale))

    im_rgb = im_rgb.resize(new_size, Image.LANCZOS)
    return im_rgb


def fetch_frame_ids(dc_pose) -> list[str]:
    """
    Fetch frame IDs for a given video based on pose confidence.

    Args:
        dc_pose: DataChain pose object.

    Returns:
        list[str]: list of frame IDs.
    """
    return [f for (f,) in dc_pose.distinct('frame.frame').to_iter('frame.frame')]


def process_frame2results(frame_file, pose_detections: list, orig_shape: tuple) -> Results:
    """
    Process a single frame to prepare for plotting.

    Args:
        frame_file: Frame file object.
        pose_detections (list): list of pose detections.
        orig_shape (tuple): Original shape of the image.

    Returns:
        Results: Processed results for plotting.
    """
    img_file_path = frame_file.get_fs_path()
    img_pil = Image.open(img_file_path)
    rgb_array = np.asarray(img_pil)
    if rgb_array.ndim == 3 and rgb_array.shape[2] == 3:
        bgr_array = rgb_array[:, :, ::-1]  # RGB to BGR conversion
    else:
        bgr_array = rgb_array  # Handle grayscale images

    boxes, keypoints = extract_yolo_results(pose_detections, orig_shape)

    return Results(
        bgr_array,
        path=img_file_path,
        names={0: 'person'},
        boxes=boxes.data,
        keypoints=keypoints.data,
    )
