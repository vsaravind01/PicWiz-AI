from fastapi import APIRouter, HTTPException, status, Depends
from db.mongo_connect import MongoConnection
from db.config import Entity
from models import Person, PersonResponse
from routers.dependencies.auth_jwt import get_current_user


router = APIRouter(prefix="/person", tags=["person"])


@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(person: PersonResponse):
    with MongoConnection(entity=Entity.PERSON) as conn:
        conn.insert(person)

    return person


@router.get(
    "/search", response_model=list[PersonResponse], status_code=status.HTTP_200_OK
)
async def search_persons(name: str, user=Depends(get_current_user)):
    with MongoConnection(entity=Entity.PERSON) as conn:
        persons = conn.find_many(
            {"name": {"$regex": name, "$options": "i"}, "owner": user.id}
        )

    return persons


@router.get(
    "/{person_id}", response_model=PersonResponse, status_code=status.HTTP_200_OK
)
async def get_person(person_id: str, user=Depends(get_current_user)):
    with MongoConnection(entity=Entity.PERSON) as conn:
        person = conn.find({"id": person_id, "owner": user.id})

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )

    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(person_id: str, user=Depends(get_current_user)):
    with MongoConnection(entity=Entity.PERSON) as conn:
        result = conn.delete({"id": person_id, "owner": user.id})

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )


@router.put(
    "/{person_id}", response_model=PersonResponse, status_code=status.HTTP_200_OK
)
async def update_person(person_id: str, person: Person):
    with MongoConnection(entity=Entity.PERSON) as conn:
        conn.update({"id": person_id}, person.model_dump())

    return person


@router.put(
    "/{person_id}/name/{name}",
    response_model=PersonResponse,
    status_code=status.HTTP_200_OK,
)
async def update_person_name(person_id: str, name: str):
    with MongoConnection(entity=Entity.PERSON) as conn:
        response = conn.update({"id": person_id}, {"name": name.lower()})

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )

    return response


@router.get("/", response_model=list[PersonResponse], status_code=status.HTTP_200_OK)
async def list_persons(limit: int = 100, page: int = 0, user=Depends(get_current_user)):
    with MongoConnection(entity=Entity.PERSON) as conn:
        persons = conn.find_many(
            {"owner": user.id}, limit=limit, page=page, fields={"centroid": 0}
        )

    return persons
