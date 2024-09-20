import io
import uuid
from typing import Type
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from fastapi.responses import Response
from PIL import Image
from sqlmodel import select

from core.embed.clip import get_clip_embedding
from datastore.base_store import BaseDataStore
from db import DBConnection, MongoConnection, SqlConnection, QdrantConnection
from db.config import Entity, QdrantCollections
from models import Face, Photo, PhotoResponse
from routers.dependencies.auth_jwt import get_current_user
from routers.dependencies.db_dependency import get_db_connection
from routers.dependencies.datastore_dependency import get_datastore

router = APIRouter(prefix="/photo", tags=["photo"])


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db_conn: Type[DBConnection] = Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    if not file.content_type or not file.content_type.startswith("image"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
        )

    id = uuid4()
    ext = file.content_type.split("/")[-1]

    blob_uri = datastore.upload(
        file=file.file,
        file_id=str(id),
        file_extension=ext,
        content_type=file.content_type,
    )
    photo = Photo(
        id=id,
        uri=blob_uri,
        owner_id=user.id,
        datastore=getattr(datastore, "datastore_type"),
    )

    with db_conn(entity=Entity.PHOTO) as conn:
        conn.insert(photo.model_dump())

    await file.seek(0)
    embedding = get_clip_embedding(Image.open(io.BytesIO(await file.read())))
    with QdrantConnection(collection=QdrantCollections.CLIP_EMBEDDINGS) as conn:
        conn.upsert(id=str(id), data=photo.model_dump(), embedding=embedding)

    return photo


@router.post("/m", response_model=list[Photo], status_code=status.HTTP_201_CREATED)
async def bulk_upload_photos(
    files: list[UploadFile] = File(...),
    db_conn: Type[DBConnection] = Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    photos = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
            )

        id = uuid4()
        ext = file.content_type.split("/")[-1]

        blob_uri = datastore.upload(
            file=file.file,
            file_id=str(id),
            file_extension=ext,
            content_type=file.content_type,
        )
        photo = Photo(
            id=id,
            uri=blob_uri,
            owner_id=datastore.user.id,
            datastore=getattr(datastore, "datastore_type"),
        )

        photos.append(photo)

    for file in files:
        await file.seek(0)

    with db_conn(entity=Entity.PHOTO) as conn:
        conn.insert_many([photo.model_dump() for photo in photos])

    with QdrantConnection(collection=QdrantCollections.CLIP_EMBEDDINGS) as conn:
        conn.upsert_many(
            ids=[photo.id for photo in photos],
            data=[photo.model_dump() for photo in photos],
            embeddings=[
                get_clip_embedding(Image.open(io.BytesIO(await file.read())))
                for file in files
            ],
        )

    return photos


@router.get("/search", response_model=list[Photo], status_code=status.HTTP_200_OK)
async def search_photos(
    query: str,
    db_conn: Type[DBConnection] = Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    with db_conn(entity=Entity.PHOTO) as conn:
        photos = conn.find_many(
            {
                "$text": {"$search": query},
                "owner_id": datastore.user.id,
                "datastore": getattr(datastore, "datastore_type"),
            },
        )

    return photos


@router.get("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def get_photo(
    photo_id: uuid.UUID,
    db_conn: Type[DBConnection] = Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    with db_conn(entity=Entity.PHOTO) as conn:
        photo = conn.find(
            {
                "id": photo_id,
                "owner_id": datastore.user.id,
                "datastore": getattr(datastore, "datastore_type"),
            },
        )

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo[0]


@router.get("/{photo_id}/download", status_code=status.HTTP_200_OK)
async def download_photo(
    photo_id: uuid.UUID,
    db_conn=Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    with db_conn(entity=Entity.PHOTO) as conn:
        photo = conn.find(
            {
                "id": photo_id,
                "owner_id": datastore.user.id,
                "datastore": getattr(datastore, "datastore_type"),
            }
        )

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    result = datastore.download(str(photo_id))
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found in storage"
        )
    content, content_type = result

    return Response(content=content, media_type=content_type)


@router.get("/{photo_id}/{field}", status_code=status.HTTP_200_OK)
async def get_photo_path(
    photo_id: uuid.UUID,
    field: str,
    db_conn: Type[DBConnection] = Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    if field not in Photo.__annotations__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Field not found"
        )
    with db_conn(entity=Entity.PHOTO) as conn:
        photo = conn.find(
            {
                "id": photo_id,
                "owner_id": datastore.user.id,
                "datastore": getattr(datastore, "datastore_type"),
            },
        )

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    return photo[0][field]


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: uuid.UUID,
    db_conn: Type[DBConnection] = Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    with db_conn(entity=Entity.PHOTO) as conn:
        result = conn.delete(
            {
                "id": photo_id,
                "owner_id": datastore.user.id,
                "datastore": getattr(datastore, "datastore_type"),
            }
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    datastore.delete(str(photo_id))


@router.get(
    "/{photo_id}/faces", response_model=list[Face], status_code=status.HTTP_200_OK
)
def get_faces_in_photo(
    photo_id: uuid.UUID,
    user=Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    with db_conn(entity=Entity.PHOTO) as conn:
        if isinstance(conn, SqlConnection):
            statement = (
                select(Face)
                .join(Photo)
                .where(Photo.id == photo_id)
                .where(Photo.owner_id == user.id)
            )
            faces = conn.execute(statement)
        elif isinstance(conn, MongoConnection):
            pipeline = [
                {"$match": {"id": photo_id, "owner_id": user.id}},
                {
                    "$lookup": {
                        "from": "Face",
                        "localField": "id",
                        "foreignField": "photo_id",
                        "as": "faces",
                    }
                },
                {"$unwind": "$faces"},
                {"$replaceRoot": {"newRoot": "$faces"}},
            ]
            faces = list(conn.collection.aggregate(pipeline))
    return faces


@router.get("/", response_model=list[Photo], status_code=status.HTTP_200_OK)
async def list_photos(
    limit: int = 100,
    page: int = 0,
    db_conn: Type[DBConnection] = Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    with db_conn(entity=Entity.PHOTO) as conn:
        photos = conn.find(
            {
                "owner_id": datastore.user.id,
                "datastore": getattr(datastore, "datastore_type"),
            },
            limit=limit,
            page=page,
        )

    return photos
