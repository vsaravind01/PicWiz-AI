from typing import Any, Generator
import numpy as np
from PIL import Image
from retinaface import RetinaFace
from torch import Tensor

from core.detect.utils import crop_resize
from core.detect.types import ImageData
from torchvision.transforms import functional as F


FACE_DETECTION_MODEL = RetinaFace.build_model()


class FaceDetector:
    def __init__(self, images: list[ImageData]):
        self.images = images

    def detect_faces(self) -> Any:
        for image in self.images:
            faces = RetinaFace.extract_faces(np.array(image.image))
            bbox = {"bbox": faces}
            image.meta.update(bbox)

    def get_faces(self, image_size: int = 160) -> Generator[tuple[ImageData, Tensor], None, None]:
        for image in self.images:
            if "bbox" in image.meta:
                for _, value in image.meta["bbox"]:
                    face_image = crop_resize(
                        np.array(image.image), value["facial_area"], image_size
                    )
                    if isinstance(face_image, np.ndarray) or isinstance(face_image, Tensor):
                        yield image, F.to_tensor(np.float32(face_image))
                    else:
                        yield image, F.to_tensor(np.array(face_image, dtype=np.float32))
