from typing import Type

from db import MongoConnection, SqlConnection, DBConnection
from settings import Settings


def get_db_connection() -> Type[DBConnection]:
    settings = Settings()
    if settings.db_type == "mongodb":
        return MongoConnection
    elif settings.db_type == "sql":
        return SqlConnection
