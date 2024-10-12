from typing import Type
from uuid import UUID

from sqlalchemy import func, or_, select
from db import DBConnection
from db.mongo_connect import MongoConnection
from db.sql_connect import SqlConnection
from .base_handler import BaseHandler
from db.config import Entity
from models import User, Person


class PersonHandler(BaseHandler):
    def __init__(self, db_conn: Type[DBConnection]):
        super().__init__(Entity.PERSON, db_conn)

    async def create_person(self, person: Person, user: User) -> dict:
        person.owner_id = user.id
        return await self.create(person.model_dump())

    async def get_persons_by_user(self, user: User, limit: int = 100, page: int = 0) -> list[dict]:
        return await self.list({"owner_id": user.id}, limit=limit, page=page)

    async def update_person(self, person_id: UUID, data: dict, user: User) -> dict:
        return await self.update(person_id, data, {"owner_id": user.id})

    async def delete_person(self, person_id: UUID, user: User) -> None:
        await self.delete(person_id, {"owner_id": user.id})

    async def get_person_faces(self, person_id: UUID, user: User) -> list[dict]:
        with self.db_conn(entity=self.entity) as conn:
            result = conn.join_query(
                main_entity=Entity.FACE,
                join_entities=[((Entity.PERSON, "id"), (Entity.FACE, "person_id"))],
                conditions={"person_id": person_id, "owner_id": user.id},
                fields={"centroid": 0},
                select_from=Entity.FACE.get_class(),
            )
        return result

    async def get_person_photos(self, person_id: UUID, user: User) -> list[dict]:
        with self.db_conn(entity=self.entity) as conn:
            result = conn.join_query(
                main_entity=Entity.PHOTO,
                join_entities=[
                    ((Entity.FACE, "photo_id"), (Entity.PHOTO, "id")),
                    ((Entity.PERSON, "id"), (Entity.FACE, "person_id")),
                ],
                conditions={"person_id": person_id, "owner_id": user.id},
                fields={"embedding": 0},
            )
        return result

    async def search_by_name(self, name: str, user: User) -> dict[UUID, list[dict]]:
        if not name:
            return {}
        with self.db_conn(entity=self.entity) as conn:
            if isinstance(conn, SqlConnection):
                session = conn.session
                name_conditions = [func.lower(Person.name).op("~")(f".*{name.lower()}.*")]
                stmt = select(Person).where(or_(*name_conditions), Person.owner_id == user.id)
                result = session.exec(stmt)
                response = [person for person in result.scalars().all()]
                session.close()
            elif isinstance(conn, MongoConnection):
                regex_pattern = f".*{name.lower()}.*"
                response = [
                    person["id"]
                    for person in conn.find(
                        {"name": {"$regex": regex_pattern, "$options": "i"}, "owner_id": user.id},
                        {"id": 1},
                    )
                ]
            else:
                raise ValueError(f"Unsupported database connection type: {type(conn)}")
            photos = {}
            for person in response:
                photos[person.name] = await self.get_person_photos(person.id, user)
            return photos
