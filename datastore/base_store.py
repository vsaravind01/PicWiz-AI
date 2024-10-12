from __future__ import annotations

from abc import ABC, abstractmethod
from models import User
from typing import BinaryIO, Optional

from types_ import DatastoreType


class BaseDataStore(ABC):
    def __init__(self, user: User, datastore_type: DatastoreType):
        self.datastore_type = datastore_type
        self.user = user

    @abstractmethod
    def upload(self, file: BinaryIO, file_id: str, file_extension: str, content_type: str) -> str:
        pass

    @abstractmethod
    def download(self, file_id: str) -> tuple[Optional[bytes | str], Optional[str]]:
        pass

    @abstractmethod
    def get_file_path(self, file_id: str) -> str:
        pass

    @abstractmethod
    def get_file_paths(self, file_ids: list[str]) -> list[str]:
        pass

    @abstractmethod
    def delete(self, file_id: str) -> bool:
        pass

    @abstractmethod
    def list_files(self) -> list[str]:
        pass

    def get_full_path(self, file_id: str, file_extension: str) -> str:
        return f"{self.user.id}/{file_id}.{file_extension}"
