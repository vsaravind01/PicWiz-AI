from core.loader.image_loader import ImageLoader
from core.detect.scene import SceneDetector
from db.mongo_connect import MongoConnection
from db.sql_connect import SqlConnection
from models import Photo
from pipeline.pipeline_runner import PipelineRunner
from db.config import Entity
from sqlalchemy import func, update
from typing import Dict, Any


class SceneDetectionRunner(PipelineRunner):
    def __init__(self):
        super().__init__("scene_detection", "scene", [Entity.PHOTO])
        self.detector = SceneDetector()

    def preprocess_func(self, img):
        self.detector.detect(img, True)
        self.logger.info(f"Scenes detected for image {img.id}")

    def execute(self, loader: ImageLoader, **kwargs) -> Dict[str, Any]:
        results = {}
        for img_id, img in loader.iter():
            results[img_id] = img.scenes

        return results

    def _update_sql(self, conn: SqlConnection, task_results: Dict[str, Any], entity: Entity):
        session = conn.session
        for img_id, scenes in task_results.items():
            scs = []
            for scene, score in scenes:
                scene = scene.replace("_", " ").lower()
                scs.append(scene)

            stmt = (
                update(Photo)
                .where(Photo.id == img_id)
                .values(scenes=scenes)
                .values(entities=func.array_cat(Photo.entities, scs))
                .values(scene_processed=True)
                .returning(Photo)
            )

            result = session.exec(stmt).all()

            if len(result) == 0:
                self.logger.error(f"Failed to update {img_id}")

        session.commit()

    def _update_mongo(self, conn: MongoConnection, task_results: Dict[str, Any], entity: Entity):
        for img_id, scenes in task_results.items():
            scs = []
            for scene, score in scenes:
                scene = scene.replace("_", " ").lower()
                scs.append(scene)

            result = conn.collection.update_one(
                {"id": img_id},
                {
                    "$set": {"scenes": scenes, "scenes_processed": True},
                    "$push": {"entities": {"$each": scs}},
                },
            )

            if result.modified_count == 0:
                self.logger.info(f"Failed to update {img_id}")

    @staticmethod
    def add_arguments(parser):
        pass


if __name__ == "__main__":
    runner = SceneDetectionRunner()
    runner.run()
