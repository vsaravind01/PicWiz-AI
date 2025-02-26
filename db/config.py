import os
from enum import Enum
from typing import Type
from models import Album, Face, Person, Photo, User, PhotoAlbumLink

class Entity(Enum):
    USER = "users"
    ALBUM = "albums"
    PHOTO = "photos"
    PERSON = "person"
    FACE = "face"
    PHOTO_ALBUM_LINK = "photo_album_link"

    def get_class(self) -> Type[User | Photo | Album | Person | Face | PhotoAlbumLink]:
        if self == Entity.USER:
            return User
        elif self == Entity.PHOTO:
            return Photo
        elif self == Entity.ALBUM:
            return Album
        elif self == Entity.PERSON:
            return Person
        elif self == Entity.FACE:
            return Face
        elif self == Entity.PHOTO_ALBUM_LINK:
            return PhotoAlbumLink
        else:
            raise ValueError("Invalid collection")


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "chatterchum")


class QdrantCollections(Enum):
    FACENET_EMBEDDINGS = "photo_embeddings"
    CLIP_EMBEDDINGS = "clip_embeddings"


QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))


SQL_DB_NAME = os.getenv("DATABASE_NAME", "chatterchum")
SQL_URI_MAP = {
    "sqlite": os.getenv("DATABASE_URL", f"sqlite:///./{SQL_DB_NAME}.db"),
    "postgres": os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://vsaravind:pass@localhost/{SQL_DB_NAME}",
    ),
}
