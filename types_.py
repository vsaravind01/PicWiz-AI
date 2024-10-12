from enum import Enum


class DBType(str, Enum):
    SQL = "sql"
    MONGODB = "mongodb"


class DatastoreType(str, Enum):
    LOCAL = "local"
    GCLOUD = "gcloud"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
