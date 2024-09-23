import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Response, status, UploadFile
from uuid import UUID

from datastore.base_store import BaseDataStore
from models import PhotoResponse, User, Photo
from routers.dependencies.auth_jwt import get_current_user
from routers.dependencies.db_dependency import get_db_connection
from routers.dependencies.datastore_dependency import get_datastore
from handlers.photo_handler import PhotoHandler

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/", response_model=list[PhotoResponse], status_code=status.HTTP_201_CREATED)
async def upload_photo(
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
    datastore: BaseDataStore = Depends(get_datastore),
):
    handler = PhotoHandler(db_conn)
    uploaded_photos = []

    for file in files:
        if not file.content_type or not file.content_type.startswith("image"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} must be an image",
            )

        photo_id = uuid.uuid4()
        blob_uri = datastore.upload(
            file=file.file,
            file_id=str(photo_id),
            file_extension=file.content_type.split("/")[-1],
            content_type=file.content_type,
        )
        photo = Photo(
            id=photo_id,
            uri=blob_uri,
            datastore=datastore.datastore_type,
            owner_id=user.id,
        )

        await file.seek(0)
        file_content = await file.read()
        photo = await handler.create_with_file(file_content, photo, user)
        uploaded_photos.append(photo)

    return uploaded_photos


@router.get("/search", response_model=list[PhotoResponse], status_code=status.HTTP_200_OK)
async def search_photos_by_term(
    term: str,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PhotoHandler(db_conn)
    return await handler.search_by_terms(term, user)


@router.get("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def get_photo(
    photo_id: UUID,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PhotoHandler(db_conn)
    return await handler.get(photo_id, filters={"owner_id": user.id})


@router.get("/{photo_id}/download", status_code=status.HTTP_200_OK)
async def download_photo(
    photo_id: UUID,
    datastore=Depends(get_datastore),
):
    content, content_type = datastore.download(str(photo_id))
    return Response(content=content, media_type=content_type)


@router.get("/", response_model=list[PhotoResponse], status_code=status.HTTP_200_OK)
async def list_photos(
    limit: int = 100,
    page: int = 0,
    db_conn=Depends(get_db_connection),
    datastore=Depends(get_datastore),
):
    handler = PhotoHandler(db_conn)
    return await handler.list(
        filters={"owner_id": datastore.user.id, "datastore": datastore.datastore_type},
        limit=limit,
        page=page,
    )


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: UUID,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
    datastore=Depends(get_datastore),
):
    handler = PhotoHandler(db_conn)
    await handler.delete(photo_id, filters={"owner_id": user.id})
    datastore.delete(str(photo_id))


@router.get("/search", response_model=list[PhotoResponse], status_code=status.HTTP_200_OK)
async def search_photos(
    query: str,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PhotoHandler(db_conn)
    return await handler.search(query, user)


@router.get("/{photo_id}/faces", response_model=list[dict], status_code=status.HTTP_200_OK)
async def get_faces_in_photo(
    photo_id: UUID,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PhotoHandler(db_conn)
    return await handler.get_faces(photo_id, user)
