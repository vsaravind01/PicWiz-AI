from typing import List, Dict, Any
from uuid import uuid4
from collections import defaultdict

from db.config import Entity
from db.mongo_connect import MongoConnection
from db.sql_connect import SqlConnection
from core.loader.image_loader import ImageLoader
from core.cluster.community_detection import CommunityDetector
from core.embed.face import FaceEmbedder
from models import Face, Person
from pipeline.pipeline_runner import PipelineRunner


class FaceClusterRunner(PipelineRunner):
    def __init__(self):
        self.embedder = FaceEmbedder()
        super().__init__("face_cluster", "faces", [Entity.PERSON, Entity.PHOTO])

    def preprocess_func(self, img):
        self.embedder.embed(img)
        self.logger.info(f"Faces embedded for image {img.id}")

    def execute(self, loader: ImageLoader, **kwargs) -> Dict[str, Any]:
        self.logger.info("Detecting communities")
        detector = CommunityDetector(
            threshold=kwargs.get("threshold", 0.7),
            min_community_size=kwargs.get("min_community_size", 2),
            init_max_size=kwargs.get("init_max_size", 5),
        )
        detector.fit(loader.image_data)

        loader.update_face_index()

        return {
            "loader": loader,
            "detector": detector,
            "user": kwargs.get("user"),
            "photos": kwargs.get("photos"),
        }

    def _update_sql(self, conn: SqlConnection, task_results: Dict[str, Any], entity: Entity):
        if entity == Entity.PERSON:
            self._update_sql_persons(conn, task_results)
        elif entity == Entity.PHOTO:
            self._update_sql_photos(conn, task_results)

    def _update_mongo(self, conn: MongoConnection, task_results: Dict[str, Any], entity: Entity):
        if entity == Entity.PERSON:
            self._update_mongo_persons(conn, task_results)
        elif entity == Entity.PHOTO:
            self._update_mongo_photos(conn, task_results)

    def _update_sql_persons(self, conn: SqlConnection, task_results: Dict[str, Any]):
        loader = task_results["loader"]
        detector = task_results["detector"]
        user = task_results["user"]

        session = conn.session
        persons = []
        photo_id_person_map = defaultdict(set)

        for cluster, centroid in zip(detector.clusters, detector.centroids):
            person_id = uuid4()
            person = Person(id=person_id, owner_id=user.id, centroid=centroid.tolist(), name=None)
            faces = []
            for photo_id, face_key in cluster:
                fid = uuid4()
                image_data = loader.image_data[photo_id]
                face = image_data.faces[face_key]
                face_obj = Face(
                    id=fid,
                    known=False,
                    embedding=self.convert_float32_list_to_float(
                        face["embedding"].flatten().tolist()
                    ),
                    score=float(face["score"]),
                    bbox=self.convert_int32_list_to_int(face["facial_area"]),
                    person=person,
                    photo_id=photo_id,
                )
                faces.append(face_obj)
                photo_id_person_map[photo_id].add(person)
            person.faces = faces
            persons.append(person)

        session.add_all(persons)
        session.commit()
        session.close()

        task_results["photo_id_person_map"] = photo_id_person_map

    def _update_mongo_persons(self, conn: MongoConnection, task_results: Dict[str, Any]):
        loader = task_results["loader"]
        detector = task_results["detector"]
        user = task_results["user"]

        persons = []
        photo_id_person_map = defaultdict(set)

        for cluster, centroid in zip(detector.clusters, detector.centroids):
            person_id = uuid4()
            person = Person(id=person_id, owner_id=user.id, centroid=centroid.tolist(), name=None)
            faces = []
            for photo_id, face_key in cluster:
                fid = uuid4()
                image_data = loader.image_data[photo_id]
                face = image_data.faces[face_key]
                face_obj = Face(
                    id=fid,
                    known=False,
                    embedding=self.convert_float32_list_to_float(
                        face["embedding"].flatten().tolist()
                    ),
                    score=float(face["score"]),
                    bbox=self.convert_int32_list_to_int(face["facial_area"]),
                    person=person,
                    photo_id=photo_id,
                )
                faces.append(face_obj)
                photo_id_person_map[photo_id].add(person)
            person.faces = faces
            persons.append(person)

        conn.insert_many([person.model_dump() for person in persons])

        task_results["photo_id_person_map"] = photo_id_person_map

    def _update_sql_photos(self, conn: SqlConnection, task_results: Dict[str, Any]):
        photo_id_person_map = task_results["photo_id_person_map"]
        photos = task_results["photos"]

        session = conn.session
        for photo in photos:
            photo.people = list(photo_id_person_map[photo.id])
            photo.faces_processed = True
            session.merge(photo)
        session.commit()
        session.close()

    def _update_mongo_photos(self, conn: MongoConnection, task_results: Dict[str, Any]):
        photo_id_person_map = task_results["photo_id_person_map"]

        for photo_id, people in photo_id_person_map.items():
            result = conn.update(
                {"id": photo_id}, {"people": list(people), "faces_processed": True}
            )
            if not result:
                self.logger.error(f"Failed to update photo {photo_id}")

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--threshold", type=float, default=0.72, help="Community detection threshold"
        )
        parser.add_argument(
            "--min_community_size",
            type=int,
            default=2,
            help="Minimum community size for community detection",
        )
        parser.add_argument(
            "--init_max_size", type=int, default=5, help="Initial max size for community detection"
        )

    @staticmethod
    def convert_float32_list_to_float(data: list):
        return [float(x) for x in data]

    @staticmethod
    def convert_int32_list_to_int(data: list):
        return [int(x) for x in data]


if __name__ == "__main__":
    runner = FaceClusterRunner()
    runner.run()
