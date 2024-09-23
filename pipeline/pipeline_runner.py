import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Union

from db.config import Entity
from db.mongo_connect import MongoConnection
from db.sql_connect import SqlConnection
from pipeline.pipeline_utils import download_images, get_user, get_user_photos, logger
from settings import Settings
from db import DB_CONNECTION_MAP
from core.loader.image_loader import ImageLoader


class PipelineRunner:

    def __init__(self, task_name: str, column: str, connection_requirements: list[Entity]):
        self.task_name = task_name
        self.column = column
        self.connection_requirements = connection_requirements
        self.settings = Settings()
        self.logger = logger

    def execute(self, loader: ImageLoader, **kwargs) -> dict[str, Any]:
        raise NotImplementedError

    def preprocess_func(self, img):
        raise NotImplementedError

    def task(self, local_file_paths: list[str], num_workers: int = 4, **kwargs):
        self.logger.info(f"Running {self.task_name}")

        loader = ImageLoader(local_file_paths, auto_load=True)
        self.logger.info("Starting preprocessing")
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(self.preprocess_func, img) for _, img in loader.iter()]
            asyncio.get_event_loop().run_until_complete(
                asyncio.gather(*[asyncio.wrap_future(f) for f in futures])
            )
        self.logger.info("Preprocessing completed")

        self.logger.info("Starting execution")
        results = self.execute(loader, **kwargs)
        self.logger.info(f"{self.task_name} execution completed")

        return results

    def update_collections(
        self,
        task_results: dict[str, Any],
        connections: dict[Entity, Union[SqlConnection, MongoConnection]],
    ):
        for entity, conn in connections.items():
            self.logger.info(f"Updating {entity.name} collection")
            if isinstance(conn, SqlConnection):
                self._update_sql(conn, task_results, entity)
            elif isinstance(conn, MongoConnection):
                self._update_mongo(conn, task_results, entity)

        self.logger.info("Collections updated")

    def _update_sql(self, conn: SqlConnection, task_results: dict[str, Any], entity: Entity):
        raise NotImplementedError

    def _update_mongo(self, conn: MongoConnection, task_results: dict[str, Any], entity: Entity):
        raise NotImplementedError

    def run(self):
        parser = argparse.ArgumentParser(description=f"{self.task_name} pipeline")
        parser.add_argument("--user-id", type=str, required=True, help="User ID")
        parser.add_argument("--num-workers", type=int, default=4, help="Number of workers")
        self.add_arguments(parser)
        args = parser.parse_args()

        user = get_user(args.user_id)
        photos = get_user_photos(user.id, self.column, self.settings.storage.datastore)
        if len(photos) == 0:
            self.logger.info("No photos to process")
            return

        local_file_paths = download_images(user, photos)

        task_results = self.task(local_file_paths, user=user, photos=photos, **vars(args))

        db_type = self.settings.db.db_type
        connection_class = DB_CONNECTION_MAP[db_type]

        connections = {}
        for entity in self.connection_requirements:
            connections[entity] = connection_class(entity=entity)

        try:
            self.update_collections(task_results, connections)
        finally:
            for conn in connections.values():
                conn.close()

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass
