import os

from sqlalchemy.engine import Engine
from sqlalchemy_utils import create_database, database_exists
from sqlmodel import create_engine, Session, SQLModel

from settings import Settings

DATABASE_NAME = os.getenv("DATABASE_NAME", "chatterchum")

DATABASE_URI_MAP = {
    "sqlite": os.getenv("DATABASE_URL", f"sqlite:///./{DATABASE_NAME}.db"),
    "postgres": os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://vsaravind:pass@localhost/{DATABASE_NAME}",
    ),
}


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)


class SingletonDBManager(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DBError(Exception):
    pass


class SqlDatabaseManager(metaclass=SingletonDBManager):
    settings = Settings()
    if settings.db_type == "sql":
        database_url = DATABASE_URI_MAP["postgres"]
        if not database_exists(database_url):
            create_database(database_url)
    pool_size = settings.pool_size
    max_overflow = settings.max_overflow

    def __init__(self):
        self._engine = None
        self._session = None

    def engine(self) -> Engine:
        try:
            if self._engine is None:
                self._engine = create_engine(
                    self.database_url,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                )
            return self._engine
        except Exception as e:
            raise DBError(f"Error creating DB engine: {e}") from e

    def session(self) -> Session:
        return Session(self.engine(), autoflush=False, autocommit=False)

    def __enter__(self) -> Session:
        self._session = self.session()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()


def get_db() -> Session:
    with SqlDatabaseManager() as db:
        yield db
