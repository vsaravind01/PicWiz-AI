import os
from enum import Enum
from models import User, Photo, Album, Face, Person


class MongoCollections(Enum):
    USER = "users"
    ALBUM = "albums"
    PHOTO = "photos"
    PERSON = "person"
    FACE = "face"

    def get_class(self):
        if self == MongoCollections.USER:
            return User
        elif self == MongoCollections.PHOTO:
            return Photo
        elif self == MongoCollections.ALBUM:
            return Album
        elif self == MongoCollections.PERSON:
            return Person
        elif self == MongoCollections.FACE:
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
