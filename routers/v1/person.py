import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from models import Person, PersonResponse, User
from handlers import PersonHandler
from models.response_models import FaceResponse, PhotoResponse
from models.tables import Face
from routers.dependencies.auth_jwt import get_current_user
from routers.dependencies.db_dependency import get_db_connection

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("/", response_model=PersonResponse)
async def create_person(
    person: Person,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PersonHandler(db_conn)
    return await handler.create_person(person, current_user)


@router.get("/", response_model=list[PersonResponse])
async def get_persons(
    current_user: User = Depends(get_current_user), db_conn=Depends(get_db_connection)
):
    handler = PersonHandler(db_conn)
    return await handler.get_persons_by_user(current_user)


@router.get(
    "/search", response_model=dict[str, list[PhotoResponse]], status_code=status.HTTP_200_OK
)
async def search_persons_by_name(
    name: str,
    user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PersonHandler(db_conn)
    return await handler.search_by_name(name, user)


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PersonHandler(db_conn)
    person = await handler.get(person_id, {"owner_id": current_user.id})
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: uuid.UUID,
    person: Person,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PersonHandler(db_conn)
    return await handler.update_person(person_id, person.model_dump(), current_user)


@router.delete("/{person_id}")
async def delete_person(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PersonHandler(db_conn)
    await handler.delete_person(person_id, current_user)
    return {"message": "Person deleted successfully"}


@router.get("/{person_id}/faces", response_model=list[FaceResponse])
async def get_person_faces(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PersonHandler(db_conn)
    return await handler.get_person_faces(person_id, current_user)


@router.get("/{person_id}/photos", response_model=list[PhotoResponse])
async def get_person_photos(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db_conn=Depends(get_db_connection),
):
    handler = PersonHandler(db_conn)
    return await handler.get_person_photos(person_id, current_user)
