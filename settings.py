import os
import json
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Type
from rich.console import Console
from rich.table import Table

from datastore import BaseDataStore, DATASTORE_MAP
from types_ import DatastoreType, DBType, LogLevel


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class DBSettings:
    db_type: DBType = DBType.SQL
    pool_size: int = 5
    max_overflow: int = 10

    def dict(self):
        return asdict(self)


@dataclass
class LocalStoreSettings:
    base_path: str = "data"

    def dict(self):
        return asdict(self)


@dataclass
class GCloudStoreSettings:
    bucket_name: str = os.environ.get("GCLOUD_BUCKET_NAME", "")
    project_id: str = os.environ.get("GCLOUD_PROJECT_ID", "")

    def dict(self):
        return asdict(self)


@dataclass
class StorageSettings:
    datastore: DatastoreType = DatastoreType.LOCAL
    local: LocalStoreSettings = field(default_factory=LocalStoreSettings)
    gcloud: GCloudStoreSettings = field(default_factory=GCloudStoreSettings)

    def dict(self):
        return {
            "datastore": self.datastore,
            "local": self.local.dict(),
            "gcloud": self.gcloud.dict(),
        }

    @property
    def datastore_class(self) -> Type[BaseDataStore]:
        return DATASTORE_MAP[self.datastore]["class"]

    @property
    def datastore_settings(self):
        try:
            return DATASTORE_MAP[self.datastore]["settings"](self)
        except KeyError:
            raise ValueError(f"Unsupported datastore type: {self.datastore}")


@dataclass
class AppConfig:
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO

    def dict(self):
        return asdict(self)


class Settings(metaclass=Singleton):
    def __init__(self):
        self.db = DBSettings()
        self.storage = StorageSettings()
        self.app = AppConfig()
        self.load()

    def load(self):
        if not os.path.exists("settings.json"):
            self.save()
        with open("settings.json", "r") as f:
            data = json.load(f)
            for section, values in data.items():
                if hasattr(self, section):
                    if section == "storage":
                        self.storage.datastore = DatastoreType(values["datastore"])
                        self.storage.local = LocalStoreSettings(**values["local"])
                        if not os.environ.get("GCLOUD_BUCKET_NAME"):
                            self.storage.gcloud.bucket_name = values["gcloud"]["bucket_name"]
                        if not os.environ.get("GCLOUD_PROJECT_ID"):
                            self.storage.gcloud.project_id = values["gcloud"]["project_id"]
                    else:
                        for key, value in values.items():
                            setattr(getattr(self, section), key, value)

    def save(self):
        data = {
            "db": self.db.dict(),
            "storage": self.storage.dict(),
            "app": self.app.dict(),
        }
        with open("settings.json", "w") as f:
            json.dump(data, f, indent=4)

    def display_settings(self, setting_type=None):
        console = Console()

        def create_table(title, data):
            table = Table(title=title, show_header=True, header_style="bold cyan")
            table.add_column("Setting", style="dim")
            table.add_column("Value")
            for key, value in data.items():
                if isinstance(value, Enum):
                    table.add_row(key, value.value)
                else:
                    table.add_row(key, str(value))
            return table

        if setting_type is None or setting_type == "db":
            console.print(create_table("Database Settings", self.db.dict()))
        if setting_type is None or setting_type == "storage":
            for key, value in self.storage.dict().items():
                if isinstance(value, dict):
                    if self.storage.datastore.value == key:
                        title = f"{key} Settings (Default)"
                    else:
                        title = f"{key} Settings"
                    console.print(create_table(title, value))
        if setting_type is None or setting_type == "app":
            console.print(create_table("Application Settings", self.app.dict()))
