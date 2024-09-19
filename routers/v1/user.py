from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from routers.dependencies import get_db_connection, get_current_user
from db.base_db_connect import DBDuplicateKeyError
from db.config import Entity
from models import User, UserResponse, Photo, Album

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/", response_model=UserResponse)
async def get_user(
    user=Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    collection = Entity.USER
    with db_conn(entity=collection) as conn:
        user = conn.find_by_id(user.id)

    return user


@router.put("/", response_model=UserResponse)
async def update_user(
    user: User,
    current_user=Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    collection = Entity.USER
    user.id = current_user.id
    with db_conn(entity=collection) as conn:
        user.hash_password()
        result = conn.update({"id": str(current_user.id)}, user.model_dump())
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    return user


@router.delete("/", response_model=UserResponse)
async def delete_user(
    current_user=Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    collection = Entity.USER
    with db_conn(entity=collection) as conn:
        result = conn.delete({"id": str(current_user.id)})
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    return current_user
