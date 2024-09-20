import uuid
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Optional

from models import Photo


class UserResponse(SQLModel, table=False):
    id: uuid.UUID
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
        unique_fields = tuple()


class FaceResponse(SQLModel, table=False):
    id: uuid.UUID
    known: bool
    score: float
    person_id: Optional[uuid.UUID]
    photo_id: uuid.UUID
    bbox: Optional[list[int]]
    # other_features: dict

    class Config:
        from_attributes = True
        unique_fields = tuple()


class PersonResponse(SQLModel, table=False):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: Optional[str] = Field(default=None)
    faces: list[str] = Field(default_factory=lambda: [])
    photos: list[Photo] = Field(default_factory=lambda: [])


class PhotoResponse(SQLModel, table=False):
    id: uuid.UUID
    uri: str
    owner_id: uuid.UUID
    objects: list[tuple[str, float]]
    scenes: list[tuple[str, float]]
    entities: list[str]
    datastore: str
