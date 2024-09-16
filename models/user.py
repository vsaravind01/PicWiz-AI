from uuid import uuid4
from pydantic import BaseModel, Field, EmailStr, field_validator
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
        unique_fields = ("email",)

    @field_validator("password", mode="before")
    @classmethod
    def set_password(cls, value: str) -> str:
        return pwd_context.hash(value)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
