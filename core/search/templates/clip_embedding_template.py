from typing import Any
from core.search.prompt_library.base import BasePromptAdapter, BasePromptGenerator
from core.search.prompt_library.factory import PromptFactory
from core.search.prompt_library.types import GeneratorType
from core.search.templates.base_template import BaseSearchTemplate
from core.search.db_ops import DatabaseOperations
from models import User
from core.embed.clip import get_clip_embedding
from db import QdrantConnection
from db.config import QdrantCollections
from collections import defaultdict


class ClipEmbeddingTemplate(BaseSearchTemplate):
    def __init__(self, adapter: BasePromptAdapter, db_ops: DatabaseOperations):
        super().__init__(name="clip_embedding", db_ops=db_ops)
        self.adapter = adapter
        self.similar_query_generator: BasePromptGenerator = PromptFactory.get_generator(
            GeneratorType.SIMILAR_QUERY, self.adapter.llm_type
        )

    async def search(self, query: str, user: User, **kwargs) -> dict[str, Any]:
        similar_queries = await self.generate_similar_queries(query, **kwargs)
        clip_results = await self._search_clip_embeddings([query] + similar_queries, **kwargs)
        return {"clip_results": clip_results, "similar_queries": similar_queries}

    async def generate_similar_queries(self, query: str, **kwargs) -> list[str]:
        prompt = self.similar_query_generator.generate(query)
        response = await self.adapter.execute_prompt(prompt, **kwargs)
        parsed_response = self.adapter.parse_response(response)
        return parsed_response["similar_queries"]

    async def _search_clip_embeddings(self, queries: list[str], top_k: int) -> list[dict[str, Any]]:
        clip_results = []
        rrf_scores = defaultdict(float)
        top_k = 60

        for query in queries:
            embedding = get_clip_embedding(query)

            with QdrantConnection(collection=QdrantCollections.CLIP_EMBEDDINGS) as conn:
                results = conn.search(embedding, top_k=top_k, threshold=0.21)

            for rank, result in enumerate(results, start=1):
                rrf_scores[result["id"]] += 1 / (top_k + rank)

        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        results = [id for id, _ in sorted_results[:5]]

        final_results = []
        for id in results:
            for query_results in clip_results:
                for result in query_results:
                    if result["id"] == id:
                        final_results.append(result)
                        break
                if len(final_results) == len(results):
                    break

        return final_results
