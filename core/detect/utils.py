import cv2
import numpy as np
import torch.nn.functional as F

from PIL import Image
from torch import Tensor

from core.detect.types import BoxType, ImageType


def imresample(img: ImageType, size):
    im_data = F.interpolate(img, size=size, mode="area")
    return im_data


def crop_resize(
    img: ImageType,
    box: BoxType,
    image_size: int = 160,
) -> ImageType:
    x = box[0]
    y = box[1]
    w = box[2] - x
    h = box[3] - y
    if isinstance(img, np.ndarray):
        img = img[y : y + h, x : x + w]
        out = cv2.resize(img, (image_size, image_size), interpolation=cv2.INTER_AREA).copy()
    elif isinstance(img, Tensor):
        img = img[y : y + h, x : x + w]
        out = (
            imresample(img.permute(2, 0, 1).unsqueeze(0).float(), (image_size, image_size))
            .byte()
            .squeeze(0)
            .permute(1, 2, 0)
        )
    else:
        out = img.crop(box).copy().resize((image_size, image_size), Image.BILINEAR)  # type: ignore
    return out
