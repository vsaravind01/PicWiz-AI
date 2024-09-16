from uuid import uuid4
from pydantic import BaseModel, Field


class Photo(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    uri: str
    owner: str
    faces_processed: bool = Field(default=False)
    objects_processed: bool = Field(default=False)
    scene_processed: bool = Field(default=False)

    objects: list[tuple[str, float]] = Field(default_factory=lambda: [])
    scenes: list[tuple[str, float]] = Field(default_factory=lambda: [])
    faces: list[str] = Field(default_factory=lambda: [])

    entities: list[str] = Field(default_factory=lambda: [])

    class Config:
        from_attributes = True
        unique_fields = ("uri",)
