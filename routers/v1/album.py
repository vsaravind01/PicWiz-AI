from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Optional
from uuid import UUID

from models import User, Album
from handlers import AlbumHandler
from models.tables import Photo
from routers.dependencies.db_dependency import get_db_connection
from routers.dependencies.auth_jwt import get_current_user

router = APIRouter()


@router.post("/albums", response_model=Album)
async def create_album(
    album: Album, current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = AlbumHandler(db_conn)
    return await handler.create_album(album, current_user)


@router.get("/albums", response_model=list[Album])
async def get_albums(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = AlbumHandler(db_conn)
    return await handler.get_albums_by_user(current_user)


@router.get("/albums/{album_id}", response_model=Album)
async def get_album(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    album = await handler.get(album_id, {"owner_id": current_user.id})
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


@router.put("/albums/{album_id}", response_model=Album)
async def update_album(
    album_id: UUID,
    album: Album,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    return await handler.update_album(album_id, album.model_dump(), current_user)


@router.delete("/albums/{album_id}")
async def delete_album(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    await handler.delete_album(album_id, current_user)
    return {"message": "Album deleted successfully"}


@router.get("/albums/{album_id}/photos", response_model=list[Photo])
async def get_album_photos(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    return await handler.get_album_photos(album_id, current_user)


@router.post("/albums/{album_id}/photos", response_model=list[UUID])
async def add_photos_to_album(
    album_id: UUID,
    photo_ids: list[UUID] = Body(...),
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    return await handler.add_photos_to_album(album_id, photo_ids, current_user)


@router.delete("/albums/{album_id}/photos", response_model=list[UUID])
async def remove_photos_from_album(
    album_id: UUID,
    photo_ids: list[UUID],
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    return await handler.remove_photos_from_album(album_id, photo_ids, current_user)


@router.get("/albums/{album_id}/cover", response_model=Optional[str])
async def get_album_cover(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    return await handler.get_album_cover(album_id, current_user)


@router.put("/albums/{album_id}/cover/{photo_id}", response_model=Album)
async def set_album_cover(
    album_id: UUID,
    photo_id: UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = AlbumHandler(db_conn)
    return await handler.set_album_cover(album_id, photo_id, current_user)
