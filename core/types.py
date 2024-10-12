from __future__ import annotations
import sys
import uuid

from typing_extensions import Annotated
from typing import Any, Generic, Optional, Sequence, TypeVar
import numpy as np
from numpy.typing import ArrayLike
from torch import Tensor, tensor
from PIL.Image import Image

from pydantic import BaseModel, field_validator, BeforeValidator, ConfigDict, PlainSerializer


BoxType = tuple[float, float, float, float] | tuple[int, int, int, int] | Sequence[float | int]


class ImageData(BaseModel):
    id: uuid.UUID
    image: Any
    meta: dict = dict()

    faces: dict = {}
    scenes: list[tuple[str, float]] = []
    objects: list[tuple[str, float]] = []

    def to_embedding_data(self, embeddings: Sequence[np.ndarray]) -> Sequence[EmbeddingData]:
        return [
            EmbeddingData(id=self.id, embedding=embedding, meta=self.meta)
            for embedding in embeddings
        ]

    def to_numpy(self) -> np.ndarray:
        return np.array(self.image)

    def to_tensor(self) -> Tensor:
        return tensor(np.array(self.image))

    def set_face_embedding(self, face_key: str, embedding: Any):
        self.faces[face_key]["embedding"] = embedding

    def set_faces(self, faces: dict):
        self.faces = faces

    def set_objects(self, objects: list[tuple[str, float]]):
        self.objects = objects

    def set_scenes(self, scenes: list[tuple[str, float]]):
        self.scenes = scenes

    def update_meta(self, meta: dict):
        self.meta.update(meta)

    @field_validator("image")
    def check_image(cls, value: Image) -> Image:
        if not isinstance(value, Image):
            raise ValueError("Image must be of type PIL.Image.Image")
        return value


class EmbeddingData(BaseModel):
    id: uuid.UUID
    embedding: Any
    meta: dict = dict()

    def model_dump(self, **kwargs) -> dict[str, Any]:
        if isinstance(self.embedding, Tensor):
            self.embedding = self.embedding.numpy()

        if not isinstance(self.embedding, list):
            self.embedding = self.embedding.tolist()

        return super().model_dump(**kwargs)
