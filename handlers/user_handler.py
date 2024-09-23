from typing import Type, Optional
from uuid import UUID

from db import DBConnection
from .base_handler import BaseHandler
from db.config import Entity
from models import User, Photo, Album, Person, Face


class UserHandler(BaseHandler):
    def __init__(self, db_conn: Type[DBConnection]):
        super().__init__(Entity.USER, db_conn)

    async def create_user(self, user: User) -> dict:
        user.hash_password()
        return await self.create(user.model_dump())

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        users = await self.list({"email": email}, limit=1)
        return users[0] if users else None

    async def update_user(self, user_id: UUID, data: dict) -> dict:
        return await self.update(user_id, data)

    async def delete_user(self, user_id: UUID) -> None:
        await self.delete(user_id)

    async def update_user_person(self, user_id: UUID, person_id: UUID) -> Optional[dict]:
        with self.db_conn(entity=Entity.PERSON) as conn:
            person = conn.find_by_id(person_id)
            if not person:
                return None

        return await self.update(user_id, {"person_id": person_id})

    async def get_user_photos(self, user_id: UUID, limit: int = 100, page: int = 0) -> list[Photo]:
        with self.db_conn(entity=Entity.PHOTO) as conn:
            photos = conn.find({"owner_id": user_id}, limit=limit, page=page)
        return [Photo(**photo) for photo in photos]

    async def get_user_albums(self, user_id: UUID, limit: int = 100, page: int = 0) -> list[Album]:
        with self.db_conn(entity=Entity.ALBUM) as conn:
            albums = conn.find({"owner_id": user_id}, limit=limit, page=page)
        return [Album(**album) for album in albums]

    async def get_user_people(self, user_id: UUID, limit: int = 100, page: int = 0) -> list[Person]:
        with self.db_conn(entity=Entity.PERSON) as conn:
            people = conn.find(
                {"owner_id": user_id},
                fields={"centroid": 0},
                limit=limit,
                page=page,
            )
        return [Person(**person) for person in people]

    async def get_user_faces(self, user_id: UUID, limit: int = 100, page: int = 0) -> list[Face]:
        with self.db_conn(entity=Entity.FACE) as conn:
            result = conn.join_query(
                main_entity=Entity.FACE,
                join_entities=[
                    ((Entity.PHOTO, "id"), (Entity.FACE, "photo_id")),
                ],
                fields={"embedding": 0},
                conditions={"owner_id": user_id, "known": False},
                limit=limit,
                page=page,
            )
        return [Face(**face) for face in result]

    async def get_user_album_photos(
        self, user_id: UUID, album_id: UUID, limit: int = 100, page: int = 0
    ) -> list[Photo]:
        with self.db_conn(entity=Entity.PHOTO) as conn:
            result = conn.join_query(
                main_entity=Entity.PHOTO,
                join_entities=[
                    ((Entity.PHOTO_ALBUM_LINK, "photo_id"), (Entity.PHOTO, "id")),
                    ((Entity.ALBUM, "id"), (Entity.PHOTO_ALBUM_LINK, "album_id")),
                ],
                conditions={"owner_id": user_id, "album_id": album_id},
                fields={"embedding": 0},
                limit=limit,
                page=page,
            )
        return [Photo(**photo) for photo in result]

    async def get_user_person_faces(
        self, user_id: UUID, person_id: UUID, limit: int = 100, page: int = 0
    ) -> list[Face]:
        with self.db_conn(entity=self.entity) as conn:
            result = conn.join_query(
                main_entity=Entity.FACE,
                join_entities=[((Entity.PERSON, "id"), (Entity.FACE, "person_id"))],
                conditions={"person_id": person_id, "owner_id": user_id},
                fields={"centroid": 0},
                select_from=Entity.FACE.get_class(),
                limit=limit,
                page=page,
            )
        return [Face(**face) for face in result]
