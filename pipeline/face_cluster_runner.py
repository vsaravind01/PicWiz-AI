import sys

sys.path.append(".")


import os
from collections import defaultdict
import numpy as np

from db.config import QdrantCollections
from db.qdrant_connect import QdrantConnection

import argparse
from typing import Optional
import logging
from uuid import uuid4

from db.mongo_connect import MongoConnection, MongoCollections
from models import User
from core.loader.image_loader import ImageLoader
from core.cluster.community_detection import CommunityDetector
from core.embed.face import FaceEmbedder
from datastore.gcloud_store import GCloudStore
from models import Face, Person

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

    logger.info(f"Downloading images of user {user_id}")

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

    return f"{LOCAL_STORAGE_PATH}/{user_id}"


def run_community_detection(
    local_file_path: str,
    threshold: float = 0.7,
    min_community_size: int = 2,
    init_max_size: int = 5,
    num_workers: int = 4,
):
    loader = ImageLoader(local_file_path, auto_load=True)
    embedder = FaceEmbedder()

    event_loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for _, img in loader.iter():
            event_loop.run_in_executor(executor, embedder.embed, img)

    detector = CommunityDetector(
        threshold=threshold,
        min_community_size=min_community_size,
        init_max_size=init_max_size,
    )
    detector.fit(loader.image_data)
    loader.update_face_index()

    return loader, detector


def convert_dict_type_from_numpy(data: dict):
    # if any value in the dictionary is np.float32, convert it to float and np.int32 to int
    for key, value in data.items():
        if isinstance(value, dict):
            convert_dict_type_from_numpy(value)
        elif isinstance(value, np.floating):
            data[key] = float(value)
        elif isinstance(value, np.integer):
            data[key] = int(value)

    return data


def convert_float32_list_to_float(data: list):
    return [float(x) for x in data]


def convert_int32_list_to_int(data: list):
    return [int(x) for x in data]


def update_collections(loader: ImageLoader, detector: CommunityDetector, user: User):
    persons: list[Person] = []
    faces: list[Face] = []
    img_id_face_id_map = defaultdict(list)
    for cluster, centroid in zip(detector.clusters, detector.centroids):
        person_id = str(uuid4())
        person = Person(id=person_id, owner=user.id, centroid=centroid.tolist(), name=None)
        face_ids = []
        img_ids = []
        for img_id, face_key in cluster:
            face_id = str(uuid4())
            face_dict = loader.get_face(img_id, face_key)
            face = Face(
                id=face_id,
                person_id=person_id,
                embedding=convert_float32_list_to_float(face_dict["embedding"].flatten().tolist()),
                score=float(face_dict["score"]),
                bbox=convert_int32_list_to_int(face_dict["facial_area"]),
                # other_features=convert_dict_type_from_numpy(face_dict["landmarks"]),
                photo_id=img_id,
            )
            face_ids.append(face_id)
            faces.append(face)
            img_id_face_id_map[img_id].append(face_id)
            img_ids.append(img_id)

        person.images = img_ids
        person.faces = face_ids
        persons.append(person)

    with MongoConnection(collection=MongoCollections.PERSON) as conn:
        conn.insert_many([person.model_dump() for person in persons])
    logger.info(f"Inserted {len(persons)} persons")

    with MongoConnection(collection=MongoCollections.FACE) as conn:
        conn.insert_many([face.model_dump() for face in faces])
    logger.info(f"Inserted {len(faces)} faces")

    with QdrantConnection(collection=QdrantCollections.FACENET_EMBEDDINGS) as conn:
        for face in faces:
            f = face.model_dump()
            f.pop("embedding")
            conn.upsert(id=face.id, data=face.model_dump(), embedding=face.embedding)

    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        for img_id, face_ids in img_id_face_id_map.items():
            result = conn.update({"id": img_id}, {"faces": face_ids})
            if not result:
                logger.error(f"Failed to update photo {img_id}")
    logger.info(f"Updated {len(img_id_face_id_map)} photos")


if __name__ == "__main__":
    cpu_count = os.cpu_count()
    if cpu_count:
        default_nproc = cpu_count - 1

    parser = argparse.ArgumentParser(description="Face clustering pipeline")
    parser.add_argument("--user-id", type=str, help="User ID")
    parser.add_argument("--bucket", type=str, help="GCloud bucket name")
    parser.add_argument("--nproc", type=int, help="Number of processes", default=default_nproc)
    parser.add_argument("--num-workers", type=int, help="Number of workers", default=4)
    parser.add_argument(
        "--threshold", type=float, help="Community detection threshold", default=0.72
    )
    parser.add_argument(
        "--min_community_size",
        type=int,
        help="Minimum community size for community detection",
        default=2,
    )
    parser.add_argument(
        "--init_max_size", type=int, help="Initial max size for community detection", default=5
    )

    args = parser.parse_args()

    bucket_name = args.bucket
    nproc = args.nproc
    num_workers = args.num_workers
    threshold = args.threshold
    min_community_size = args.min_community_size
    init_max_size = args.init_max_size

    with MongoConnection(collection=MongoCollections.USER) as conn:
        user = conn.find({"id": args.user_id})

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

    loader, detector = run_community_detection(
        local_file_path=local_file_path,
        threshold=threshold,
        min_community_size=min_community_size,
        init_max_size=init_max_size,
        num_workers=num_workers,
    )

    update_collections(loader, detector, user_obj)
