from typing import Any
from qdrant_client import QdrantClient, models

from db.config import QDRANT_PORT, QDRANT_HOST, QdrantCollections


class QdrantConnection:
    def __init__(self, collection: QdrantCollections) -> None:
        self._client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.collection_name = collection.value
        if not self._client.collection_exists(collection.value):
            self._client.create_collection(
                collection_name=collection.value,
                vectors_config=models.VectorParams(
                    size=512,
                    distance=models.Distance.COSINE,
                ),
            )

    def __del__(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()

    def upsert(self, id: str, data: dict, embedding: list[float]) -> None:
        self._client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=id,
                    payload=data,
                    vector=embedding,
                )
            ],
        )

    def search(self, embedding: list[float], top_k: int = 10) -> list[dict]:
        results = self._client.search(
            collection_name=self.collection_name,
            score_threshold=0.21,
            query_vector=embedding,
            limit=top_k,
        )
        response = []
        for result in results:
            payload = result.payload
            if payload:
                payload["score"] = result.score
                response.append(payload)
        return response

    def upsert_many(self, ids: list[str], data: list[dict], embeddings: list[list[float]]) -> None:
        self._client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=id,
                    payload=payload,
                    vector=embedding,
                )
                for id, payload, embedding in zip(ids, data, embeddings)
            ],
        )
