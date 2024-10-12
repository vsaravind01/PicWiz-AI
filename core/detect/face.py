from typing import Any
import numpy as np
from retinaface import RetinaFace

from core.detect.base import BaseDetector
from core.types import ImageData


class FaceDetector(BaseDetector):
    def detect(self, image_data: ImageData, with_return: bool = False) -> Any:
        faces = RetinaFace.detect_faces(np.array(image_data.image), threshold=0.999)
        image_data.set_faces(faces)

        if with_return:
            return faces
