from datastore.base_store import BaseDataStore
from datastore.local_store import LocalStore
from datastore.gcloud_store import GCloudStore
from types_ import DatastoreType

DATASTORE_MAP = {
    DatastoreType.LOCAL: {
        "class": LocalStore,
        "settings": lambda self: {"base_path": self.local.base_path},
    },
    DatastoreType.GCLOUD: {
        "class": GCloudStore,
        "settings": lambda self: {
            "bucket_name": self.gcloud.bucket_name,
            "project_id": self.gcloud.project_id,
        },
    },
}
