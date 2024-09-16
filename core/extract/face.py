from abc import ABC, abstractmethod
from typing import Generator
import numpy as np
from core.extract.utils import extract_face
from core import types
from core.detect.face import FaceDetector


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, image_data: types.ImageData, with_image_data: bool = False):
        raise NotImplementedError


class FaceExtractor(BaseExtractor):
    detector = FaceDetector()

    def extract(
        self, image_data: types.ImageData, with_key: bool = False
    ) -> Generator[np.ndarray | tuple[np.ndarray, str], None, None]:
        if not image_data.faces:
            self.detector.detect(image_data)
        for face_key, face in image_data.faces.items():
            if with_key:
                yield extract_face(image_data.image, face["facial_area"]), face_key
            else:
                yield extract_face(image_data.image, face["facial_area"])
