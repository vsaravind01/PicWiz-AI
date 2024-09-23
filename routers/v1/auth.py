from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from routers.dependencies import get_db_connection
from db.errors import DBDuplicateKeyError
from db.config import Entity
from models import User
from routers.dependencies.auth_jwt import create_jwt_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    email: str = Body(...),
    password: str = Body(...),
    db_conn=Depends(get_db_connection),
):

    user = db_conn(entity=Entity.USER).find({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user = user[0]
    if not User.verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    token = create_jwt_token(user["email"])

    response = JSONResponse(content={"token": token}, status_code=status.HTTP_200_OK)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600,
    )

    return response


@router.post("/signup")
async def signup(user: User, db_conn=Depends(get_db_connection)):
    with db_conn(entity=Entity.USER) as conn:
        try:
            user.hash_password()
            conn.insert(user.model_dump())
        except DBDuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )

    return JSONResponse(
        content={"message": "User created"}, status_code=status.HTTP_201_CREATED
    )


@router.post("/logout")
async def logout():
    response = JSONResponse(
        content={"message": "Logged out"}, status_code=status.HTTP_200_OK
    )
    response.delete_cookie("token")

    return response
