from typing import Optional, Type, List
from uuid import UUID
from db import DBConnection
from .base_handler import BaseHandler
from db.config import Entity
from models import User


class FaceHandler(BaseHandler):
    def __init__(self, db_conn: Type[DBConnection]):
        super().__init__(Entity.FACE, db_conn)

    async def get_faces_by_photo(self, photo_id: UUID, user: User) -> List[dict]:
        with self.db_conn(entity=self.entity) as conn:
            faces = conn.find({"photo_id": photo_id, "owner_id": user.id})
        return faces

    async def get_faces_by_person(self, person_id: UUID, user: User) -> List[dict]:
        with self.db_conn(entity=self.entity) as conn:
            faces = conn.find({"person_id": person_id, "owner_id": user.id})
        return faces

    async def assign_person_to_face(self, face_id: UUID, person_id: UUID, user: User) -> dict:
        with self.db_conn(entity=self.entity) as conn:
            updated_face = conn.update(
                {"id": face_id, "owner_id": user.id}, {"person_id": person_id}
            )
        return updated_face

    async def remove_person_from_face(self, face_id: UUID, user: User) -> dict:
        with self.db_conn(entity=self.entity) as conn:
            updated_face = conn.update({"id": face_id, "owner_id": user.id}, {"person_id": None})
        return updated_face

    async def list(
        self,
        filters: Optional[dict] = None,
        limit: int = 100,
        page: int = 0,
        user_id: Optional[UUID] = None,
    ) -> List[dict]:
        with self.db_conn(entity=self.entity) as conn:
            if user_id:
                conditions = {"person.owner_id": user_id}
                if filters:
                    conditions.update(filters)
                items = conn.join_query(
                    main_entity=Entity.FACE,
                    join_entities=[((Entity.PERSON, "id"), (Entity.FACE, "person_id"))],
                    conditions=conditions,
                    limit=limit,
                    page=page,
                )
                return items
            else:
                items = conn.find(filters or {}, limit=limit, page=page)
                return items
