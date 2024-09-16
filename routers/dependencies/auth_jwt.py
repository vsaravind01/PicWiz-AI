import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from db.mongo_connect import MongoConnection
from db.config import MongoCollections
from models.user import User
import jwt

from fastapi import Depends, HTTPException, status, Cookie

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 60 * 24


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str = Cookie(None)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized-CODE1")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized-CODE2")


def get_current_user(token: str = Cookie(None)) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is required")
    payload = verify_jwt_token(token)
    collection = MongoCollections.USER
    user = MongoConnection(collection=collection).find({"email": payload["sub"]})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unauthorized")
    return User(**user)
