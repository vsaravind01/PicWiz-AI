import uuid
from typing import Any, Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from sqlmodel import SQLModel

from db.base_db_connect import DBConnection, DBDuplicateKeyError
from db.config import Entity, MONGO_DATABASE, MONGO_URI


class MongoConnection(DBConnection):
    def __init__(self, entity: Entity, database: str = MONGO_DATABASE) -> None:
        super().__init__(entity)
        self._client = MongoClient(MONGO_URI)
        self._db = self._client[database]

        if entity not in self._db.list_collection_names():
            unique_indexes = entity.get_class().Config.unique_fields
            for index in unique_indexes:
                self._db[entity.value].create_index(index, unique=True, background=True)

        self.collection = self._db[entity.value]

    def connect(self):
        return self

    def close(self) -> None:
        self._client.close()

    def get_database(self) -> Database:
        return self._db

    def insert(self, data: dict) -> None:
        try:
            for key, value in data.items():
                if isinstance(value, SQLModel):
                    data[key] = value.dict()
                elif isinstance(value, uuid.UUID):
                    data[key] = str(value)

            self.collection.insert_one(data)
        except DuplicateKeyError:
            raise DBDuplicateKeyError

    def insert_many(self, data: list[dict]) -> None:
        data = [item for item in data]
        self.collection.insert_many(data)

    def find(
        self,
        query: Any,
        fields: Optional[dict] = None,
        limit: int = 100,
        page: int = 0,
    ) -> list[dict]:
        skip = page * limit
        return list(self.collection.find(query, fields).skip(skip).limit(limit))

    def find_by_id(self, id: uuid.UUID) -> dict:
        return self.collection.find_one({"id": id})

    def count(self, query: dict) -> int:
        return self.collection.count_documents(query)

    def update(self, query: Any, data: dict, override_set: bool = False) -> dict:
        if override_set:
            return self.collection.find_one_and_update(
                query, data, return_document=True
            )
        return self.collection.find_one_and_update(
            query, {"$set": data}, return_document=True
        )

    def delete(self, query: dict) -> dict:
        return self.collection.find_one_and_delete(query)
