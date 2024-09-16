from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from db.mongo_connect import MongoConnection
from db.config import MongoCollections
from models import Face
from models.face import FaceResponse
from routers.dependencies.auth_jwt import get_current_user


router = APIRouter(prefix="/face", tags=["face"])


@router.post("/", response_model=FaceResponse, status_code=status.HTTP_201_CREATED)
async def create_face(face: Face):
    with MongoConnection(collection=MongoCollections.FACE) as conn:
        conn.insert(face.model_dump())

    return face


@router.get("/{face_id}", response_model=FaceResponse, status_code=status.HTTP_200_OK)
async def get_face(face_id: str):
    with MongoConnection(collection=MongoCollections.FACE) as conn:
        face = conn.find({"id": face_id}, {"embedding": 0})

    if not face:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Face not found")

    return face


@router.delete("/{face_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_face(face_id: str):
    with MongoConnection(collection=MongoCollections.FACE) as conn:
        result = conn.delete({"id": face_id})

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Face not found")


@router.put("/{face_id}", response_model=FaceResponse, status_code=status.HTTP_200_OK)
async def update_face(face_id: str, face: Face):
    with MongoConnection(collection=MongoCollections.FACE) as conn:
        conn.update({"id": face_id}, face.model_dump())

    return face
