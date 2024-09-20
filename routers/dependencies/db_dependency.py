from typing import Type

from db import DB_CONNECTION_MAP, DBConnection
from settings import Settings
from types_ import DBType


def get_db_connection() -> Type[DBConnection]:
    settings = Settings().db
    return DB_CONNECTION_MAP[settings.db_type]
