import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from google.cloud import storage
import uuid
from typing import Optional
from db import DB_CONNECTION_MAP
from db.config import Entity
from datastore import BaseDataStore
from models import User, Photo
from settings import Settings
from types_ import DatastoreType

logging.basicConfig(level=logging.INFO)
logging.getLogger("passlib").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

LOCAL_STORAGE_PATH = "./data/images"


def download_image(bucket_name: str, file_path: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.download_to_filename(f"{LOCAL_STORAGE_PATH}/{file_path}")
    logger.info(f"Downloaded {file_path}")


def download_batch(batch_index: int, bucket_name: str, file_paths: list[str], num_workers: int = 4):
    event_loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for file_path in file_paths:
            event_loop.run_in_executor(executor, download_image, bucket_name, file_path)
    logger.info(f"Batch {batch_index} downloaded - {len(file_paths)} images")


def download_images(user: User, photos: list[Photo]) -> list[str]:
    settings = Settings()
    datastore_class = settings.storage.datastore_class
    datastore_settings = settings.storage.datastore_settings
    datastore: BaseDataStore = datastore_class(user, **datastore_settings)

    local_path = f"{LOCAL_STORAGE_PATH}/{user.id}"

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    file_paths = []
    for photo in photos:
        fid = str(photo.id)
        fpath = datastore.get_file_path(fid)
        if fpath.startswith("http"):
            content, content_type = datastore.download(fid)
            if content and content_type:
                ext = content_type.split("/")[-1]
                local_path = f"{local_path}/{fid}.{ext}"
                with open(local_path, "wb") as f:
                    f.write(content)
                logger.info(f"Downloaded {fid}")
                file_paths.append(local_path)
        else:
            file_paths.append(fpath)
            logger.info(f"Using local file {fid}")

    return file_paths


def get_user(user_id: str) -> User:
    settings = Settings()
    db_type = settings.db.db_type
    connection_class = DB_CONNECTION_MAP[db_type]

    with connection_class(entity=Entity.USER) as conn:
        user = conn.find({"id": user_id})

    if not user:
        logger.error("User not found")
        exit(1)

    user = user[0]
    return User(**user)


def get_file_paths(user: User) -> list[str]:
    settings = Settings()
    datastore_class = settings.storage.datastore_class
    datastore_settings = settings.storage.datastore_settings
    datastore: BaseDataStore = datastore_class(user, **datastore_settings)
    return datastore.list_files()


def get_user_photos(
    user_id: uuid.UUID, column: str, datastore: Optional[DatastoreType] = None
) -> list[Photo]:
    settings = Settings()
    db_type = settings.db.db_type
    connection_class = DB_CONNECTION_MAP[db_type]

    with connection_class(entity=Entity.PHOTO) as conn:
        query: dict[str, Any] = {
            "owner_id": user_id,
            f"{column}_processed": False,
            "datastore": datastore,
        }

        if datastore is not None:
            query["datastore"] = datastore

        photos = conn.find(query)

    return [Photo(**photo) for photo in photos]
