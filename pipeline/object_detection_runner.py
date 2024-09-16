import sys

sys.path.append(".")

import os
import argparse
from typing import Optional
import logging

from db.mongo_connect import MongoConnection, MongoCollections
from models import User
from core.loader.image_loader import ImageLoader
from core.detect.object import ObjectDetector
from datastore.gcloud_store import GCloudStore

from google.cloud import storage

import multiprocessing
import asyncio

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


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


def download_images(
    bucket_name: str,
    file_paths: list[str],
    num_workers: int = 4,
    nproc: Optional[int] = None,
):
    if not os.path.exists(LOCAL_STORAGE_PATH):
        os.makedirs(LOCAL_STORAGE_PATH)

    user_id = file_paths[0].split("/")[0]
    if not os.path.exists(f"{LOCAL_STORAGE_PATH}/{user_id}"):
        os.makedirs(f"{LOCAL_STORAGE_PATH}/{user_id}")

    if nproc is None:
        nproc = multiprocessing.cpu_count() - 1

    if len(file_paths) > nproc:
        batch_size, remainder = divmod(len(file_paths), nproc)
        batches = [file_paths[i : i + batch_size] for i in range(0, len(file_paths), batch_size)]
        for i in range(remainder):
            batches[i].append(file_paths[-i - 1])

        with ProcessPoolExecutor(max_workers=nproc) as executor:
            for i, batch in enumerate(batches):
                logger.info(f"Downloading batch {i} - {len(batch)} images")
                executor.submit(download_batch, i, bucket_name, batch, num_workers)
    else:
        download_batch(0, bucket_name, file_paths, num_workers)

    return LOCAL_STORAGE_PATH


def detect_objects(local_file_path: str):
    loader = ImageLoader(local_file_path, auto_load=True)
    detector = ObjectDetector()

    logger.info("Detecting objects")
    event_loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        for _, img in loader.iter():
            event_loop.run_in_executor(executor, detector.detect, img, True)
    logger.info("Objects detected")

    return loader


def update_collections(loader: ImageLoader):
    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        for img_id, img in loader.image_data.items():
            objs = []
            objects = img.objects
            for i, obj in enumerate(objects):
                o, score = obj
                o = o.replace("_", " ").lower()
                objects[i] = (o, score)
                objs.append(o)
            result = conn.update(
                {"id": img_id},
                {"$set": {"objects": img.objects}, "$push": {"entities": {"$each": objs}}},
                override_set=True,
            )
            if not result:
                logger.info(f"Failed to update {img_id}")

    logger.info("Collections updated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process images")
    parser.add_argument("--user-id", type=str, help="User ID")
    parser.add_argument("--bucket", type=str, help="GCloud bucket name")
    parser.add_argument("--num_workers", type=int, default=4, help="Number of workers")
    parser.add_argument("--nproc", type=int, default=None, help="Number of processes")

    args = parser.parse_args()

    user_id = args.user_id
    bucket_name = args.bucket
    nproc = args.nproc
    num_workers = args.num_workers

    with MongoConnection(collection=MongoCollections.USER) as conn:
        user = conn.find({"id": user_id})

    if not user:
        logger.error("User not found")
        exit(1)

    user_obj = User(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        password=user["password"],
    )

    gcloud_store = GCloudStore(bucket_name=bucket_name, user=user_obj)

    file_paths = gcloud_store.list_files()

    local_file_path = download_images(
        bucket_name=bucket_name,
        file_paths=file_paths,
        num_workers=num_workers,
        nproc=nproc,
    )

    loader = detect_objects(local_file_path)
    update_collections(loader)
