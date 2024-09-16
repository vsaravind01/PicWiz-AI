from abc import ABC, abstractmethod

import torch
import numpy as np
from deepface.modules.modeling import build_model
from deepface.modules.preprocessing import resize_image, normalize_input

from core.types import ImageData
from core.extract.face import FaceExtractor


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, image: ImageData, with_return: bool = False):
        raise NotImplementedError


class FaceEmbedder(BaseEmbedder):
    FaceNet = build_model(task="facial_recognition", model_name="Facenet512")
    target_size = FaceNet.input_shape
    extractor = FaceExtractor()

    def get_embedding(self, img):
        img = np.array(img)
        img = img[:, :, ::-1]
        img = resize_image(img, target_size=(self.target_size[1], self.target_size[0]))
        img = normalize_input(img=img, normalization="Facenet2018")
        embedding = self.FaceNet.forward(img)

        return torch.tensor(embedding).unsqueeze(0).numpy()

    def embed(self, image_data: ImageData, with_return: bool = False):
        for face, key in self.extractor.extract(image_data, with_key=True):
            embedding = self.get_embedding(face)
            image_data.set_face_embedding(key, embedding)

        if with_return:
            return image_data.faces

    @staticmethod
    def cosine_similarity(a: torch.Tensor, b: torch.Tensor) -> float:
        return torch.nn.functional.cosine_similarity(a, b).item()
