from __future__ import annotations

from abc import ABC, abstractmethod
from models import User
from typing import BinaryIO, Optional, List


class BaseDataStore(ABC):
    def __init__(self, user: User):
        self.user = user

    @abstractmethod
    def upload(self, file: BinaryIO, file_id: str, file_extension: str, content_type: str) -> str:
        pass

    @abstractmethod
    def download(self, file_id: str) -> tuple[Optional[bytes], Optional[str]]:
        pass

    @abstractmethod
    def get_file_path(self, file_id: str) -> str:
        pass

    @abstractmethod
    def get_file_paths(self, file_ids: List[str]) -> List[str]:
        pass

    @abstractmethod
    def delete(self, file_id: str) -> bool:
        pass

    @abstractmethod
    def list_files(self) -> List[str]:
        pass

    def get_full_path(self, file_id: str, file_extension: str) -> str:
        return f"{self.user.id}/{file_id}.{file_extension}"
