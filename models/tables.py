import uuid
from typing import Optional, Annotated

from pydantic import EmailStr
from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    Enum,
    Column,
    Float,
    Integer,
    String,
    JSON,
)
from sqlalchemy.dialects import postgresql
from passlib.context import CryptContext
from models.link_tables import PhotoAlbumLink
from types_ import DatastoreType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    email: Annotated[str, EmailStr] = Field(unique=True)
    password: str = Field(nullable=False)

    photos: list["Photo"] = Relationship(back_populates="owner")
    albums: list["Album"] = Relationship(back_populates="owner")

    class Config:
        unique_fields = (
            "id",
            "email",
        )

    def hash_password(self):
        self.password = pwd_context.hash(self.password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        print(plain_password, hashed_password)
        return pwd_context.verify(plain_password, hashed_password)


class Face(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    known: bool = Field(default=False)

    embedding: list[float] = Field(
        sa_column=Column(postgresql.ARRAY(Float()), nullable=False),
    )
    score: float = Field(nullable=False)
    bbox: list[int] = Field(
        sa_column=Column(postgresql.ARRAY(Integer()), nullable=False)
    )

    photo_id: uuid.UUID = Field(foreign_key="photo.id")
    person_id: Optional[uuid.UUID] = Field(default=None, foreign_key="person.id")

    person: Optional["Person"] = Relationship(back_populates="faces")
    photo: "Photo" = Relationship(back_populates="faces")

    def __hash__(self):
        return hash(self.id)

    class Config:
        unique_fields = ("id",)


class Person(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: Optional[str] = Field(default=None)

    centroid: list[float] = Field(sa_column=Column(postgresql.ARRAY(Float()), nullable=False))

    owner_id: uuid.UUID = Field(nullable=False, foreign_key="user.id")

    photos: list["Photo"] = Relationship(back_populates="people", link_model=Face)
    faces: list[Face] = Relationship(back_populates="person")

    def __hash__(self):
        return hash(self.id)

    class Config:
        unique_fields = ("id",)


class Photo(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    uri: str = Field(nullable=False, unique=True)
    faces_processed: bool = Field(default=False)
    objects_processed: bool = Field(default=False)
    scene_processed: bool = Field(default=False)
    datastore: DatastoreType = Field(sa_column=Column(Enum(DatastoreType), nullable=False))

    objects: list[tuple[str, float]] = Field(
        default_factory=lambda: [], sa_column=Column(JSON)
    )
    scenes: list[tuple[str, float]] = Field(
        default_factory=lambda: [], sa_column=Column(JSON)
    )
    entities: list[str] = Field(
        default_factory=lambda: [], sa_column=Column(postgresql.ARRAY(String()))
    )

    owner_id: uuid.UUID = Field(nullable=False, foreign_key="user.id")

    owner: User = Relationship(back_populates="photos")
    people: list[Person] = Relationship(back_populates="photos", link_model=Face)
    faces: list[Face] = Relationship(back_populates="photo")
    albums: list["Album"] = Relationship(
        back_populates="photos", link_model=PhotoAlbumLink
    )

    class Config:
        unique_fields = ("id", "uri")


class Album(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(default=None)

    cover: Optional[str] = Field(default=None)
    ai_generated: bool = Field(default=False)

    owner_id: uuid.UUID = Field(nullable=False, foreign_key="user.id")
    owner: User = Relationship(back_populates="albums")
    photos: list[Photo] = Relationship(
        back_populates="albums", link_model=PhotoAlbumLink
    )

    class Config:
        from_attributes = True
        unique_fields = ("id",)
