from typing import Any
from core.search.templates.base_template import BaseSearchTemplate
from core.search.db_ops import DatabaseOperations
from models import User
from core.search.prompt_library import (
    PromptFactory,
    BasePromptAdapter,
    BasePromptGenerator,
    GeneratorType,
)


class SemanticParsingTemplate(BaseSearchTemplate):
    def __init__(self, adapter: BasePromptAdapter, db_ops: DatabaseOperations):
        super().__init__(name="semantic_parsing", db_ops=db_ops)
        self.llm_type = adapter.llm_type
        self.adapter = adapter
        self.semantic_parsing_generator: BasePromptGenerator = PromptFactory.get_generator(
            GeneratorType.SEMANTIC_PARSING, self.llm_type
        )

    async def parse_query(
        self, query: str, max_tokens: int = 500, temperature: float = 0.2
    ) -> dict[str, Any]:
        prompt = self.semantic_parsing_generator.generate(query)
        response = await self.adapter.execute_prompt(
            prompt, max_tokens=max_tokens, temperature=temperature
        )
        parsed_response = self.adapter.parse_response(response)
        return parsed_response

    async def search(self, query: str, user: User, **kwargs) -> dict[str, Any]:
        parsed_query = await self.parse_query(query)
        search_results = await self.db_ops.search_database(parsed_query, user, **kwargs)

        flattened_results = {"entities": {}, "photos": {}}
        for entity, entity_data in search_results["entities"].items():
            flattened_results["entities"][entity] = entity_data
        for photo_id, photo_data in search_results["photos"].items():
            flattened_results["photos"][photo_id] = photo_data

        return {"search_results": flattened_results}
