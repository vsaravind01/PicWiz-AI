import io
from uuid import uuid4

from PIL import Image
from core.embed.clip import get_clip_embedding
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import Response
from db.mongo_connect import MongoConnection
from db.qdrant_connect import QdrantConnection
from db.config import MongoCollections, QdrantCollections
from models import Photo
from models.face import Face
from routers.dependencies.auth_jwt import get_current_user
from routers.v1.utils import init_gcloud_store


router = APIRouter(prefix="/photo", tags=["photo"])


@router.post("/", response_model=Photo, status_code=status.HTTP_201_CREATED)
async def upload_photo(file: UploadFile = File(...), user=Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

    datastore = init_gcloud_store(user)
    id = str(uuid4())

    ext = file.content_type.split("/")[-1]

    embedding = get_clip_embedding(Image.open(io.BytesIO(await file.read())))

    blob_uri = datastore.upload(
        file=file.file, id=f"{id}.{ext}", content_type=file.content_type, rewind=True
    )
    photo = Photo(
        id=id,
        uri=blob_uri,
        owner=user.id,
    )

    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        conn.insert(photo.model_dump())

    with QdrantConnection(collection=QdrantCollections.CLIP_EMBEDDINGS) as conn:
        conn.upsert(id=id, data=photo.model_dump(), embedding=embedding)

    return photo


@router.get("/search", response_model=list[Photo], status_code=status.HTTP_200_OK)
async def search_photos(query: str, user=Depends(get_current_user)):
    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        photos = conn.find_many(
            {"$text": {"$search": query}, "owner": user.id},
        )

    return photos


@router.get("/{photo_id}", response_model=Photo, status_code=status.HTTP_200_OK)
async def get_photo(photo_id: str, user=Depends(get_current_user)):
    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        photo = conn.find({"id": photo_id, "owner": user.id}, fields={"clip_embedding": 0})

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    return photo


@router.get("/{photo_id}/download", status_code=status.HTTP_200_OK)
async def download_photo(photo_id: str, user=Depends(get_current_user)):
    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        photo = conn.find({"id": photo_id, "owner": user.id})

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    datastore = init_gcloud_store(user)
    blob, content_type = datastore.download(photo_id)

    return Response(content=blob, media_type=content_type)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: str, user=Depends(get_current_user)):
    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        result = conn.delete({"id": photo_id, "owner": user.id})

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    datastore = init_gcloud_store(user)
    datastore.delete(photo_id)


@router.get("/{photo_id}/faces", response_model=list[Face], status_code=status.HTTP_200_OK)
def get_faces_in_photo(photo_id: str, user=Depends(get_current_user)):
    with MongoConnection(collection=MongoCollections.FACE) as conn:
        faces = conn.find_many(
            {"photo_id": photo_id, "owner": user.id},
            fields={"embedding": 0, "other_features": 0},
        )

    return faces


@router.get("/", response_model=list[Photo], status_code=status.HTTP_200_OK)
async def list_photos(limit: int = 100, page: int = 0, user=Depends(get_current_user)):
    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        photos = conn.find_many(
            {"owner": user.id}, fields={"clip_embedding": 0}, limit=limit, page=page
        )

    return photos


@router.post("/m", response_model=list[Photo], status_code=status.HTTP_201_CREATED)
async def bulk_upload_photos(files: list[UploadFile] = File(...), user=Depends(get_current_user)):
    datastore = init_gcloud_store(user)
    photos = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
            )

        id = str(uuid4())

        ext = file.content_type.split("/")[-1]

        blob_uri = datastore.upload(
            file=file.file, id=f"{id}.{ext}", content_type=file.content_type, rewind=True
        )
        photo = Photo(
            id=id,
            uri=blob_uri,
            owner=user.id,
        )

        photos.append(photo)

    for file in files:
        file.file.seek(0)

    with MongoConnection(collection=MongoCollections.PHOTO) as conn:
        conn.insert_many([photo.model_dump() for photo in photos])

    with QdrantConnection(collection=QdrantCollections.CLIP_EMBEDDINGS) as conn:
        conn.upsert_many(
            ids=[photo.id for photo in photos],
            data=[photo.model_dump() for photo in photos],
            embeddings=[
                get_clip_embedding(Image.open(io.BytesIO(await file.read()))) for file in files
            ],
        )

    return photos
