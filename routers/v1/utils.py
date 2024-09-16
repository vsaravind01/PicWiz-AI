from datastore.gcloud_store import GCloudStore
from models import User


def init_gcloud_store(user: User, bucket_name: str = "chatterchum-photo-store"):
    return GCloudStore(bucket_name=bucket_name, user=user)
