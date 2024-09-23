from uuid import UUID
from fastapi import APIRouter, status, Depends
from models import Face, FaceResponse, User
from routers.dependencies.auth_jwt import get_current_user
from routers.dependencies.db_dependency import get_db_connection
from handlers.face_handler import FaceHandler

router = APIRouter(prefix="/face", tags=["face"])


@router.post("/", response_model=FaceResponse, status_code=status.HTTP_201_CREATED)
async def create_face(
    face: Face,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = FaceHandler(db_conn)
    face_data = face.model_dump()
    face_data["owner_id"] = user.id
    return await handler.create(face_data)


@router.get("/{face_id}", response_model=FaceResponse, status_code=status.HTTP_200_OK)
async def get_face(
    face_id: UUID,
    db_conn=Depends(get_db_connection),
):
    handler = FaceHandler(db_conn)
    return await handler.get(face_id)


@router.delete("/{face_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_face(
    face_id: UUID,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = FaceHandler(db_conn)
    await handler.delete(face_id, filters={"owner_id": user.id})


@router.put("/{face_id}", response_model=FaceResponse, status_code=status.HTTP_200_OK)
async def update_face(
    face_id: UUID,
    face: Face,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = FaceHandler(db_conn)
    face_data = face.model_dump()
    face_data["owner_id"] = user.id
    return await handler.update(face_id, face_data, filters={"owner_id": user.id})


@router.get("/", response_model=list[FaceResponse], status_code=status.HTTP_200_OK)
async def list_faces(
    limit: int = 100,
    page: int = 0,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = FaceHandler(db_conn)
    return await handler.list(
        filters={"known": False},
        limit=limit,
        page=page,
        user_id=user.id,
    )
