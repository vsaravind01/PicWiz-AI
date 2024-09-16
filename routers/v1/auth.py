from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from db.mongo_connect import MongoConnection
from db.config import MongoCollections
from models.user import User
from routers.dependencies.auth_jwt import create_jwt_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    email: str = Body(...),
    password: str = Body(...),
):
    collection = MongoCollections.USER

    user = MongoConnection(collection=collection).find({"email": email})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not User.verify_password(password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    token = create_jwt_token({"sub": user["email"]})

    response = JSONResponse(content={"token": token}, status_code=status.HTTP_200_OK)
    response.set_cookie("token", token)

    return response


@router.post("/signup")
async def signup(user: User):
    with MongoConnection(collection=MongoCollections.USER) as conn:
        conn.insert(user.model_dump())

    return JSONResponse(content={"message": "User created"}, status_code=status.HTTP_201_CREATED)


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"}, status_code=status.HTTP_200_OK)
    response.delete_cookie("token")

    return response
