from google.cloud import storage
from typing import BinaryIO, Optional
from models import User


class GCloudStore:
    def __init__(self, bucket_name: str, user: User):
        self.bucket_name = bucket_name
        self.client = storage.Client()

        self.user = user

        if not self.client.lookup_bucket(bucket_name):
            self.client.create_bucket(bucket_name)

        self.bucket = self.client.bucket(bucket_name)

    def upload(self, file: BinaryIO, id: str, **kwargs):
        blob = self.bucket.blob(self.get_blob_id(id))
        blob.upload_from_file(file, **kwargs)
        return self.get_blob_uri(id)

    def download(self, id: str) -> Optional[tuple[bytes, str]]:
        blobs = self.bucket.list_blobs(prefix=self.get_blob_id(id))
        blobs = list(blobs)
        if not blobs:
            return None
        blob_id = blobs[0].name
        content_type = blobs[0].content_type
        blob = self.bucket.blob(blob_id)
        return blob.download_as_bytes(), content_type

    def delete(self, id):
        blob = self.bucket.blob(self.get_blob_id(id))
        blob.delete()

    def list_files(self) -> list[str]:
        files = []
        user_id = self.user.id
        for blob in self.bucket.list_blobs(prefix=user_id):
            files.append(blob.name)
        return files

    def get_blob(self, id):
        return self.bucket.blob(self.get_blob_id(id))

    def get_blob_uri(self, id) -> str:
        return f"gs://{self.bucket_name}/{self.user.id}/{id}"

    def get_blob_id(self, id) -> str:
        return f"{self.user.id}/{id}"
