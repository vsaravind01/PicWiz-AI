import numpy as np

from PIL import Image

from core.types import BoxType


def crop_resize(img, box, image_size):
    out = img.crop(box).copy().resize((image_size, image_size), Image.BILINEAR)
    return out


def extract_face(img: Image.Image, box: BoxType, image_size=160, margin=0) -> np.ndarray:
    margin = [
        margin * (box[2] - box[0]) / (image_size - margin),
        margin * (box[3] - box[1]) / (image_size - margin),
    ]
    raw_image_size = img.size
    box = [
        int(max(box[0] - margin[0] / 2, 0)),
        int(max(box[1] - margin[1] / 2, 0)),
        int(min(box[2] + margin[0] / 2, raw_image_size[0])),
        int(min(box[3] + margin[1] / 2, raw_image_size[1])),
    ]

    face = crop_resize(img, box, image_size)

    face = np.array(face, dtype=np.float32)

    return face
