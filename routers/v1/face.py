from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from db.mongo_connect import MongoConnection
from db.config import Entity
from models import Face
from models import FaceResponse


router = APIRouter(prefix="/face", tags=["face"])


@router.post("/", response_model=FaceResponse, status_code=status.HTTP_201_CREATED)
async def create_face(face: Face):
    with MongoConnection(entity=Entity.FACE) as conn:
        conn.insert(face.model_dump())

    return face


@router.get("/{face_id}", response_model=FaceResponse, status_code=status.HTTP_200_OK)
async def get_face(face_id: str):
    with MongoConnection(entity=Entity.FACE) as conn:
        face = conn.find({"id": face_id}, {"embedding": 0})

    if not face:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Face not found"
        )

    return face


@router.delete("/{face_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_face(face_id: str):
    with MongoConnection(entity=Entity.FACE) as conn:
        result = conn.delete({"id": face_id})

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Face not found"
        )


@router.put("/{face_id}", response_model=FaceResponse, status_code=status.HTTP_200_OK)
async def update_face(face_id: str, face: Face):
    with MongoConnection(entity=Entity.FACE) as conn:
        conn.update({"id": face_id}, face.model_dump())

    return face
