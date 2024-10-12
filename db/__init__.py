# isort:skip_file
from typing import Type

from db.base_db_connect import DBConnection
from db.mongo_connect import MongoConnection
from db.qdrant_connect import QdrantConnection
from db.sql_db_manager import SqlDatabaseManager, get_db
from db.sql_connect import SqlConnection
from db import config

from types_ import DBType


DB_CONNECTION_MAP: dict[DBType, Type[DBConnection]] = {
    DBType.MONGODB: MongoConnection,
    DBType.SQL: SqlConnection,
}
