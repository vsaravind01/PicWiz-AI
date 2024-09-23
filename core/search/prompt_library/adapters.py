import json
import cohere
from core.search.prompt_library.base import BasePromptAdapter
from core.search.prompt_library.types import PromptResult, LLMType, GeneratorType


class CohereAdapter(BasePromptAdapter):
    def __init__(self, client: cohere.Client, model: str):
        if model not in LLMType.COHERE.available_models[GeneratorType.SEMANTIC_PARSING]:
            raise ValueError(f"Unsupported model: {model}")
        self.client = client
        self.model = model
        self.llm_type = LLMType.COHERE

    def generate_prompt(self, query: str) -> str:
        return query

    async def execute_prompt(self, prompt: str, **kwargs) -> str:
        response = self.client.chat(
            model=self.model,
            message=prompt,
            response_format={"type": "json_object"},  # type: ignore
            **kwargs,
        )
        return response.text

    def parse_response(self, response: str) -> PromptResult:
        return json.loads(response)
