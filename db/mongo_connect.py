from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from db.config import MONGO_URI, MONGO_DATABASE, MongoCollections


class MongoConnection:
    def __init__(self, collection: MongoCollections, database: str = MONGO_DATABASE) -> None:
        self._client = MongoClient(MONGO_URI)
        self._db = self._client[database]

        if collection not in self._db.list_collection_names():
            unique_indexes = collection.get_class().Config.unique_fields
            for index in unique_indexes:
                self._db[collection.value].create_index(index, unique=True, background=True)

        self.collection = self._db[collection.value]

    def __del__(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()

    def get_database(self) -> Database:
        return self._db

    def insert(self, data: dict) -> None:
        self.collection.insert_one(data)

    def insert_many(self, data: list[dict]) -> None:
        self.collection.insert_many(data)

    def find(self, query: dict, fields: Optional[dict] = None) -> Optional[dict]:
        return self.collection.find_one(query, fields)

    def find_many(
        self, query: dict, fields: Optional[dict] = None, limit: int = 100, page: int = 0
    ) -> list[dict]:
        skip = page * limit
        return list(self.collection.find(query, fields).skip(skip).limit(limit))

    def count(self, query: dict) -> int:
        return self.collection.count_documents(query)

    def update(self, query: dict, data: dict, override_set: bool = False) -> dict:
        if override_set:
            return self.collection.find_one_and_update(query, data, return_document=True)
        return self.collection.find_one_and_update(query, {"$set": data}, return_document=True)

    def update_many(self, query: dict, data: dict) -> None:
        self.collection.update_many(query, {"$set": data})

    def delete(self, query: dict) -> dict:
        return self.collection.find_one_and_delete(query)

    def delete_many(self, query: dict) -> None:
        self.collection.delete_many(query)

    def close(self) -> None:
        self._client.close()
