from typing import Optional
from sqlalchemy import Engine

from db import SqlDatabaseManager
from db.sql_db_manager import create_db_and_tables
from alembic.config import Config
from alembic import command
from settings import Settings
from types_ import DBType


def init_db() -> Optional[Engine]:
    settings = Settings().db
    if settings.db_type == DBType.SQL:
        db_manager = SqlDatabaseManager()
        engine = db_manager.engine()
        create_db_and_tables(engine)

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

        return engine
