import os
from enum import Enum

from models import Album, Face, Person, Photo, User


class Entity(Enum):
    USER = "users"
    ALBUM = "albums"
    PHOTO = "photos"
    PERSON = "person"
    FACE = "face"

    def get_class(self):
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
        else:
            raise ValueError("Invalid collection")


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "chatterchum")


class QdrantCollections(Enum):
    FACENET_EMBEDDINGS = "photo_embeddings"
    CLIP_EMBEDDINGS = "clip_embeddings"


QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
