from typing import Type, Optional
from uuid import UUID
from fastapi import HTTPException, status
from db import DBConnection
from db.config import Entity
from db.errors import DBDuplicateKeyError


class BaseHandler:
    def __init__(self, entity: Entity, db_conn: Type[DBConnection]):
        self.entity = entity
        self.db_conn = db_conn

    async def create(self, data: dict) -> dict:
        with self.db_conn(entity=self.entity) as conn:
            try:
                conn.insert(data)
                return data
            except DBDuplicateKeyError as _:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{self.entity.value} already exists",
                )

    async def get(self, id: UUID, filters: Optional[dict] = None) -> Optional[dict]:
        default_filters = {"id": id}
        if filters:
            default_filters.update(filters)
        with self.db_conn(entity=self.entity) as conn:
            item = conn.find(default_filters)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.entity.value} not found"
                )
            return item[0] if isinstance(item, list) else item

    async def list(
        self, filters: Optional[dict] = None, limit: int = 100, page: int = 0
    ) -> list[dict]:
        with self.db_conn(entity=self.entity) as conn:
            items = conn.find(filters or {}, limit=limit, page=page)
            return items

    async def update(self, id: UUID, data: dict, filters: Optional[dict] = None) -> dict:
        filters = {"id": id}
        if filters:
            filters.update(filters)
        with self.db_conn(entity=self.entity) as conn:
            item = conn.update(filters, data)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.entity.value} not found"
                )
            return item

    async def delete(self, id: UUID, filters: Optional[dict] = None) -> None:
        filters = {"id": id}
        if filters:
            filters.update(filters)
        with self.db_conn(entity=self.entity) as conn:
            result = conn.delete(filters)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.entity.value} not found"
                )
