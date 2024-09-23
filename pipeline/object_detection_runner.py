from core.detect.object import ObjectDetector
from db.mongo_connect import MongoConnection
from db.sql_connect import SqlConnection
from models import Photo
from pipeline.pipeline_runner import PipelineRunner
from db.config import Entity
from sqlalchemy import func, update
from typing import Any


class ObjectDetectionRunner(PipelineRunner):
    def __init__(self):
        super().__init__("object_detection", "objects", [Entity.PHOTO])
        self.detector = ObjectDetector()

    def preprocess_func(self, img):
        self.detector.detect(img, True)
        self.logger.info(f"Objects detected for image {img.id}")

    def execute(self, loader, **kwargs):
        result = {}
        for img_id, img in loader.image_data.items():
            objects = []
            for obj, score in img.objects:
                objects.append((obj.replace("_", " ").lower(), score))
            result[img_id] = objects
        return result

    def _update_sql(self, conn: SqlConnection, task_results: dict[str, Any], entity: Entity):
        session = conn.session
        for img_id, objects in task_results.items():
            objs = []
            for obj, score in objects:
                objs.append(obj)

            stmt = (
                update(Photo)
                .where(Photo.id == img_id)  # type: ignore
                .values(objects=objects)
                .values(entities=func.array_cat(Photo.entities, objs))
                .values(objects_processed=True)
                .returning(Photo)
            )

            result = session.exec(stmt).all()  # type: ignore

            if len(result) == 0:
                self.logger.error(f"Failed to update {img_id}")

        session.commit()
        session.close()

    def _update_mongo(self, conn: MongoConnection, task_results: dict[str, Any], entity: Entity):
        for img_id, objects in task_results.items():
            objs = []
            for obj, score in objects:
                objs.append(obj)

            result = conn.collection.update_one(
                {"id": img_id},
                {
                    "$set": {"objects": objects, "objects_processed": True},
                    "$push": {"entities": {"$each": objs}},
                },
            )

            if result.modified_count == 0:
                self.logger.info(f"Failed to update {img_id}")

    @staticmethod
    def add_arguments(parser):
        pass


if __name__ == "__main__":
    runner = ObjectDetectionRunner()
    runner.run()
