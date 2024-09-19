from datastore.gcloud_store import GCloudStore
from models import User


def init_gcloud_store(user: User):
    return GCloudStore(user=user)
