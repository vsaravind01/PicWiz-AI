from abc import ABC, abstractmethod
from typing import Any
from models import User
from core.search.db_ops import DatabaseOperations


class BaseSearchTemplate(ABC):
    def __init__(self, name: str, db_ops: DatabaseOperations):
        self.name = name
        self.db_ops = db_ops

    @abstractmethod
    async def search(self, query: str, user: User) -> dict[str, Any]:
        pass
