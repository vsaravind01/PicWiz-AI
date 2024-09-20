import uuid
from sqlmodel import SQLModel, Field

class PhotoAlbumLink(SQLModel, table=True):
    photo_id: uuid.UUID = Field(foreign_key="photo.id", primary_key=True)
    album_id: uuid.UUID = Field(foreign_key="album.id", primary_key=True)
