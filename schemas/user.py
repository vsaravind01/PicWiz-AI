from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str = Field(..., min_length=8)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
