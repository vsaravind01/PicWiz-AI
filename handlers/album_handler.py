from typing import Type
from uuid import UUID

from sqlalchemy import or_, select
from db import DBConnection
from db.mongo_connect import MongoConnection
from db.sql_connect import SqlConnection
from .base_handler import BaseHandler
from db.config import Entity
from models import User, Album
from fastapi import HTTPException


class AlbumHandler(BaseHandler):
    def __init__(self, db_conn: Type[DBConnection]):
        super().__init__(Entity.ALBUM, db_conn)

    async def create_album(self, album: Album, user: User) -> dict:
        album.owner_id = user.id
        return await self.create(album.model_dump())

    async def get_albums_by_user(self, user: User, limit: int = 100, page: int = 0) -> list[dict]:
        return await self.list({"owner_id": user.id}, limit=limit, page=page)

    async def update_album(self, album_id: UUID, data: dict, user: User) -> dict:
        return await self.update(album_id, data)

    async def delete_album(self, album_id: UUID, user: User) -> None:
        result = await self.delete(album_id, {"owner_id": user.id})
        if result == 0:
            raise HTTPException(status_code=404, detail="Album not found")

    async def get_album_photos(self, album_id: UUID, user: User) -> list[dict]:
        with self.db_conn(entity=self.entity) as conn:
            result = conn.join_query(
                main_entity=Entity.ALBUM,
                join_entities=[
                    ((Entity.PHOTO_ALBUM_LINK, "album_id"), (Entity.ALBUM, "id")),
                    ((Entity.PHOTO, "id"), (Entity.PHOTO_ALBUM_LINK, "photo_id")),
                ],
                conditions={"id": album_id, "owner_id": user.id},
                select_from=Entity.ALBUM.get_class(),
            )
        return result

    async def add_photos_to_album(
        self, album_id: UUID, photo_ids: list[UUID], user: User
    ) -> list[UUID]:
        with self.db_conn(entity=Entity.ALBUM) as conn:
            album = conn.find_by_id(album_id)
            if not album or album.owner_id != user.id:
                raise HTTPException(status_code=404, detail="Album not found")

        with self.db_conn(entity=Entity.PHOTO_ALBUM_LINK) as conn:
            links = [{"album_id": album_id, "photo_id": photo_id} for photo_id in photo_ids]
            conn.insert_many(links)

        return photo_ids

    async def remove_photos_from_album(
        self, album_id: UUID, photo_ids: list[UUID], user: User
    ) -> list[UUID]:
        with self.db_conn(entity=Entity.PHOTO_ALBUM_LINK) as conn:
            album = conn.find_by_id(album_id)
            if not album or album.owner_id != user.id:
                raise HTTPException(status_code=404, detail="Album not found")

            for photo_id in photo_ids:
                conn.delete({"album_id": album_id, "photo_id": photo_id})

        return photo_ids

    async def get_album_cover(self, album_id: UUID, user: User) -> str:
        with self.db_conn(entity=self.entity) as conn:
            album = conn.find_by_id(album_id)
            if not album or album.owner_id != user.id:
                raise HTTPException(status_code=404, detail="Album not found")

            return album.cover

    async def set_album_cover(self, album_id: UUID, photo_id: UUID, user: User) -> dict:
        with self.db_conn(entity=self.entity) as conn:
            album = conn.find_by_id(album_id)
            if not album or album.owner_id != user.id:
                raise HTTPException(status_code=404, detail="Album not found")

            with self.db_conn(entity=Entity.PHOTO) as photo_conn:
                photo = photo_conn.find_by_id(photo_id)
                if not photo or photo.owner_id != user.id:
                    raise HTTPException(status_code=404, detail="Photo not found")

            result = conn.update({"id": album_id}, {"cover": photo.id})
            if result:
                album.cover = photo.id
                return album
            else:
                raise HTTPException(status_code=404, detail="Failed to set album cover")

    async def search_by_description(self, description: str, user: User) -> list[dict]:
        with self.db_conn(entity=self.entity) as conn:
            if isinstance(conn, SqlConnection):
                stmt = select(Album).where(
                    or_(
                        Album.name.ilike(f"%{description}%"),
                        Album.description.ilike(f"%{description}%"),
                    ),
                    Album.owner_id == user.id,
                )
                result = conn.execute(stmt)
                return [album.dict() for album in result.scalars().all()]
            elif isinstance(conn, MongoConnection):
                return conn.find(
                    {
                        "$or": [
                            {"name": {"$regex": description, "$options": "i"}},
                            {"description": {"$regex": description, "$options": "i"}},
                        ],
                        "owner_id": user.id,
                    }
                )
            else:
                raise ValueError(f"Unsupported database connection type: {type(conn)}")
