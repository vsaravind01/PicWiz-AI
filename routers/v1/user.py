from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Annotated
from uuid import UUID

from handlers.person_handler import PersonHandler
from models import User, UserResponse, Photo, Album, Person, Face
from handlers import UserHandler
from routers.dependencies.auth_jwt import get_current_user
from routers.dependencies.db_dependency import get_db_connection

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = UserHandler(db_conn)
    user = await handler.get(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/", response_model=UserResponse)
async def update_current_user(
    user_data: User,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = UserHandler(db_conn)
    updated_user = await handler.update_user(
        current_user.id, user_data.model_dump(exclude={"id", "password"})
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/users/")
async def delete_current_user(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = UserHandler(db_conn)
    await handler.delete_user(current_user.id)
    return {"message": "User deleted successfully"}


@router.patch("/users/person/me")
async def update_user_person(
    person_id: Annotated[UUID, Body(embed=True)],
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    person_handler = PersonHandler(db_conn)
    person = await person_handler.get(person_id, {"owner_id": current_user.id})
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    handler = UserHandler(db_conn)
    updated_user = await handler.update_user_person(current_user.id, person_id)
    updated_person = await person_handler.update_person(
        person_id, {"name": current_user.name}, current_user
    )
    if not updated_user or not updated_person:
        raise HTTPException(status_code=404, detail="User or Person not found")
    return {"message": "User's person updated successfully"}


@router.get("/users/photos", response_model=list[Photo])
async def get_user_photos(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = UserHandler(db_conn)
    return await handler.get_user_photos(current_user.id)


@router.get("/users/albums", response_model=list[Album])
async def get_user_albums(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = UserHandler(db_conn)
    return await handler.get_user_albums(current_user.id)


@router.get("/users/people", response_model=list[Person])
async def get_user_people(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = UserHandler(db_conn)
    return await handler.get_user_people(current_user.id)


@router.get("/users/faces", response_model=list[Face])
async def get_user_faces(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = UserHandler(db_conn)
    return await handler.get_user_faces(current_user.id)


@router.get("/users/albums/{album_id}/photos", response_model=list[Photo])
async def get_user_album_photos(
    album_id: UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = UserHandler(db_conn)
    return await handler.get_user_album_photos(current_user.id, album_id)


@router.get("/users/people/{person_id}/faces", response_model=list[Face])
async def get_user_person_faces(
    person_id: UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = UserHandler(db_conn)
    return await handler.get_user_person_faces(current_user.id, person_id)
