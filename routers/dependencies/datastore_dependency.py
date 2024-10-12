from fastapi import Depends
from settings import Settings
from models import User
from routers.dependencies.auth_jwt import get_current_user
from datastore.base_store import BaseDataStore


def get_datastore(user: User = Depends(get_current_user)) -> BaseDataStore:
    settings = Settings()
    datastore_class = settings.storage.datastore_class
    datastore = datastore_class(user=user, **settings.storage.datastore_settings)
    return datastore
