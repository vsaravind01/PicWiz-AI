import base64
from google.cloud import storage
from typing import Optional, BinaryIO
from datastore import BaseDataStore
from models import User
from datetime import timedelta
from types_ import DatastoreType


class GCloudStore(BaseDataStore):
    def __init__(self, user: User, bucket_name: str, project_id: str):
        super().__init__(user, DatastoreType.GCLOUD)
        self.bucket_name = bucket_name
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def upload(self, file: BinaryIO, file_id: str, file_extension: str, content_type: str) -> str:
        full_path = self.get_full_path(file_id, file_extension)
        blob = self.bucket.blob(full_path)
        blob.upload_from_file(file, content_type=content_type)
        return full_path

    def download(self, file_id: str) -> tuple[Optional[str], Optional[str]]:
        blob = self.get_blob(file_id)
        if not blob:
            return None, None
        content = blob.download_as_bytes()
        content = base64.b64encode(content).decode("utf-8")
        file_extension = blob.name.split(".")[-1]
        return content, f"image/{file_extension}"

    def get_file_path(self, file_id: str) -> str:
        blob = self.get_blob(file_id)
        if not blob:
            return ""
        return blob.generate_signed_url(
            version="v4", expiration=timedelta(minutes=15), method="GET"
        )

    def get_file_paths(self, file_ids: list[str]) -> list[str]:
        return [self.get_file_path(file_id) for file_id in file_ids]

    def delete(self, file_id: str) -> bool:
        blob = self.get_blob(file_id)
        if blob:
            blob.delete()
            return True
        return False

    def list_files(self) -> list[str]:
        return [
            blob.name.split("/")[-1] for blob in self.bucket.list_blobs(prefix=f"{self.user.id}/")
        ]

    def get_blob(self, file_id: str):
        blobs = list(self.bucket.list_blobs(prefix=f"{self.user.id}/{file_id}"))
        return blobs[0] if blobs else None
