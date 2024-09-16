from uuid import uuid4
from typing import Optional
from pydantic import BaseModel, Field


class Person(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: Optional[str] = Field(default=None)

    owner: str
    centroid: list[float]
    faces: list[str] = Field(default_factory=lambda: [])
    images: list[str] = Field(default_factory=lambda: [])

    class Config:
        from_attributes = True
        unique_fields = tuple()


class PersonResponse(BaseModel):
    id: str
    name: Optional[str] = Field(default=None)
    faces: list[str] = Field(default_factory=lambda: [])
    images: list[str] = Field(default_factory=lambda: [])

    class Config:
        from_attributes = True
        unique_fields = tuple()
