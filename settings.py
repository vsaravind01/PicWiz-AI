import os
import json
from typing import Any, Literal

from pydantic import BaseModel
import datastore


DATASTORE_CLASS_MAP = {
    "local": datastore.LocalStore,
    "gcloud": datastore.GCloudStore,
}


class Settings(BaseModel):
    db_type: Literal["sql", "mongodb"] = "mongodb"
    pool_size: int = 5
    max_overflow: int = 10
    datastore: str = "local"

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.load()

    @property
    def datastore_class(self):
        return DATASTORE_CLASS_MAP[self.datastore]

    def load(self):
        if not os.path.exists("settings.json"):
            self.save()
        with open("settings.json", "r") as f:
            data = json.load(f)
            self.db_type = data["db_type"]
            self.pool_size = data["pool_size"]
            self.max_overflow = data["max_overflow"]
            self.datastore = data["datastore"]

    def save(self):
        with open("settings.json", "w") as f:
            json.dump(self.model_dump(), f, indent=4)
