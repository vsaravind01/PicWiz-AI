from uuid import UUID
from typing import Type

from sqlalchemy import select, text
from db import DBConnection
from db.config import Entity, QdrantCollections
from db.mongo_connect import MongoConnection
from db.sql_connect import SqlConnection
from models import User
from models.tables import Photo
from .base_handler import BaseHandler
from db import QdrantConnection
from core.embed.clip import get_clip_embedding
from PIL import Image
import io


class PhotoHandler(BaseHandler):
    def __init__(self, db_conn: Type[DBConnection]):
        super().__init__(Entity.PHOTO, db_conn)

    async def create_with_file(self, file_data: bytes, photo: Photo, user: User) -> dict:
        photo.owner_id = user.id
        response = await self.create(photo.model_dump())

        embedding = get_clip_embedding(Image.open(io.BytesIO(file_data)))
        with QdrantConnection(collection=QdrantCollections.CLIP_EMBEDDINGS) as conn:
            conn.upsert(id=str(photo.id), data=photo.model_dump(), embedding=embedding)

        return response

    async def search(self, query: str, user: User) -> list[dict]:
        photos = await self.list({"owner_id": user.id})
        return [photo for photo in photos if query.lower() in photo["uri"].lower()]

    async def get_faces(self, photo_id: UUID, user: User) -> list[dict]:
        with self.db_conn(entity=Entity.PHOTO) as conn:
            result = conn.join_query(
                main_entity=Entity.FACE,
                join_entities=[((Entity.PHOTO, "id"), (Entity.FACE, "photo_id"))],
                conditions={"photo_id": photo_id, "owner_id": user.id},
                fields={"embedding": 0},
            )
        return result

    async def search_by_terms(self, term: str, user: User) -> list[dict]:
        if not term:
            return []
        with self.db_conn(entity=self.entity) as conn:
            if isinstance(conn, SqlConnection):
                session = conn.session
                conditions = []
                conditions.append(f"element ~* '{term}'")
                where_clause = " or ".join(conditions)
                stmt = select(Photo).where(
                    Photo.owner_id == user.id,
                    text(
                        f"exists(select 1 from unnest(photo.entities) as element where {where_clause})"
                    ),
                )
                result = session.exec(stmt)
                response = [photo for photo in result.scalars().all()]
                session.close()
                return response
            elif isinstance(conn, MongoConnection):
                result = conn.collection.find(
                    {
                        "$or": [
                            {"scenes": {"$elemMatch": {"$regex": term, "$options": "i"}}},
                            {"objects": {"$elemMatch": {"$regex": term, "$options": "i"}}},
                            {"entities": {"$elemMatch": {"$regex": term, "$options": "i"}}},
                        ]
                    },
                    {"owner_id": user.id},
                )
                return list(result)
            else:
                raise ValueError(f"Unsupported database connection type: {type(conn)}")
