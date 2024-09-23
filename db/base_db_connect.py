from typing import Optional, List, Tuple, Dict
import uuid
from abc import ABC, abstractmethod

from db.config import Entity


class BaseConnection(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def insert(self, data: dict):
        pass

    @abstractmethod
    def insert_many(self, data: list[dict]):
        pass

    @abstractmethod
    def find(self, query: dict, fields: Optional[dict] = None, limit: int = 100, page: int = 0):
        pass

    @abstractmethod
    def find_by_id(self, id: uuid.UUID):
        pass

    @abstractmethod
    def count(self, query: dict):
        pass

    @abstractmethod
    def update(self, id: uuid.UUID, data: dict, override_set: bool = False):
        pass

    @abstractmethod
    def delete(self, query: dict):
        pass

    @abstractmethod
    def join_query(
        self,
        main_entity: Entity,
        join_entities: List[Tuple[Tuple[Entity, str], Tuple[Entity, str]]],
        conditions: Dict,
        fields: Optional[Dict] = None,
        limit: int = 100,
        page: int = 0,
    ):
        pass


class DBConnection(BaseConnection):

    def __init__(self, entity: Entity):
        self.entity = entity

    def __del__(self):
        self.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def insert(self, data: dict):
        raise NotImplementedError

    def insert_many(self, data: list[dict]):
        raise NotImplementedError

    def find(self, query: dict, fields: Optional[dict] = None, limit: int = 100, page: int = 0):
        raise NotImplementedError

    def find_by_id(self, id: uuid.UUID):
        raise NotImplementedError

    def count(self, query: dict):
        raise NotImplementedError

    def update(self, query: dict, data: dict, override_set: bool = False):
        raise NotImplementedError

    def delete(self, query: dict):
        raise NotImplementedError

    def join_query(
        self,
        main_entity: Entity,
        join_entities: List[Tuple[Tuple[Entity, str], Tuple[Entity, str]]],
        conditions: Dict,
        fields: Optional[Dict] = None,
        limit: int = 100,
        page: int = 0,
    ):
        raise NotImplementedError
