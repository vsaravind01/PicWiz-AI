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
        query: dict,
        fields: Optional[dict] = None,
        limit: int = 100,
        page: int = 0,
    ) -> list[dict]:
        skip = page * limit
        converted_query = self._convert_uuid_in_query(query)
        return list(self.collection.find(converted_query, fields).skip(skip).limit(limit))

    def find_by_id(self, id: uuid.UUID) -> Optional[dict]:
        return self.collection.find_one({"id": str(id)})

    def count(self, query: dict) -> int:
        converted_query = self._convert_uuid_in_query(query)
        return self.collection.count_documents(converted_query)

    def update(self, query: dict, data: dict, override_set: bool = False) -> dict:
        converted_query = self._convert_uuid_in_query(query)
        for key, value in data.items():
            if isinstance(value, uuid.UUID):
                data[key] = str(value)

        if override_set:
            return self.collection.find_one_and_update(converted_query, data, return_document=True)
        return self.collection.find_one_and_update(
            converted_query, {"$set": data}, return_document=True
        )

    def delete(self, query: dict) -> dict:
        converted_query = self._convert_uuid_in_query(query)
        return self.collection.find_one_and_delete(converted_query)

    @staticmethod
    def _convert_uuid_in_query(query: dict) -> dict:
        converted_query = {}
        for key, value in query.items():
            if isinstance(value, uuid.UUID):
                converted_query[key] = str(value)
            elif isinstance(value, dict):
                converted_query[key] = MongoConnection._convert_uuid_in_query(value)
            else:
                converted_query[key] = value
        return converted_query
