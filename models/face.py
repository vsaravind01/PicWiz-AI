from uuid import uuid4
from typing import Optional
from pydantic import BaseModel, Field


class Face(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    known: bool = Field(default=False)

    embedding: list[float]
    score: float

    person_id: Optional[str] = None

    photo_id: str
    bbox: Optional[list[int]] = None
    # other_features: dict = Field(default_factory=lambda: {})

    class Config:
        from_attributes = True
        unique_fields = tuple()


class FaceResponse(BaseModel):
    id: str
    known: bool
    score: float
    person_id: Optional[str]
    photo_id: str
    bbox: Optional[list[int]]
    # other_features: dict

    class Config:
        from_attributes = True
        unique_fields = tuple()
