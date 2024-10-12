import os
import base64
from typing import Optional, BinaryIO
from datastore import BaseDataStore
from models import User
from types_ import DatastoreType


class LocalStore(BaseDataStore):
    def __init__(self, user: User, base_path: str):
        super().__init__(user, DatastoreType.LOCAL)
        self.base_path = base_path
        self.user_path = os.path.join(self.base_path, str(self.user.id))
        os.makedirs(self.user_path, exist_ok=True)

    def upload(self, file: BinaryIO, file_id: str, file_extension: str, content_type: str) -> str:
        full_path = self.get_full_path(file_id, file_extension)
        file_path = os.path.join(self.base_path, full_path)
        with open(file_path, "wb") as f:
            f.write(file.read())
        return file_path

    def download(self, file_id: str) -> tuple[Optional[str], Optional[str]]:
        file_path = self.get_file_path(file_id)
        if not os.path.exists(file_path):
            return None, None
        with open(file_path, "rb") as f:
            content = f.read()
        content = base64.b64encode(content).decode("utf-8")
        file_extension = os.path.splitext(file_path)[1][1:]
        return content, f"image/{file_extension}"

    def get_file_path(self, file_id: str) -> str:
        for file in os.listdir(self.user_path):
            if file.startswith(file_id):
                return os.path.join(self.user_path, file)
        return ""

    def get_file_paths(self, file_ids: list[str]) -> list[str]:
        return [self.get_file_path(file_id) for file_id in file_ids]

    def delete(self, file_id: str) -> bool:
        file_path = self.get_file_path(file_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def list_files(self) -> list[str]:
        return [
            f for f in os.listdir(self.user_path) if os.path.isfile(os.path.join(self.user_path, f))
        ]

    def get_full_path(self, file_id: str, file_extension: str) -> str:
        return f"{self.user.id}/{file_id}.{file_extension}"
