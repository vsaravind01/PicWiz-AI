from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class Album(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    description: str
    cover: Optional[str]
    photos: list[str] = []

    ai_generated: bool = Field(default=False)

    class Config:
        from_attributes = True
        unique_fields = tuple()

    def model_dump(self, **kwargs) -> dict[str, Any]:
        if not self.cover:
            self.cover = self.photos[0]
        return super().model_dump(**kwargs)
