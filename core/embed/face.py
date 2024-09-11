from typing import Generator
from facenet_pytorch import InceptionResnetV1
from torch import Tensor
import torch.nn.functional as F
from core.detect.face import FaceDetector
from core.detect.types import ImageData


class FaceEmbedder:
    model = InceptionResnetV1(pretrained="vggface2").eval()

    def __init__(self, face_detector: FaceDetector):
        self.face_detector = face_detector

    def embed_faces(self) -> Generator[tuple[ImageData, Tensor], None, None]:
        for image, face in self.face_detector.get_faces():
            yield image, self.model(face.unsqueeze(0))

    def embed(self) -> Generator[ImageData, None, None]:
        for image, face in self.embed_faces():
            image.meta.update({"embedding": face})
            yield image

    @staticmethod
    def cosine_similarity(a: Tensor, b: Tensor) -> float:
        return F.cosine_similarity(a, b).item()
