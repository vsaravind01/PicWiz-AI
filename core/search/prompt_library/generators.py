from .base import BasePromptGenerator
from .prompts import get_prompt
from .types import LLMType, PromptType


class SemanticParsingGenerator(BasePromptGenerator):
    def __init__(self, llm_type: LLMType):
        self.llm_type = llm_type

    def generate(self, query: str) -> str:
        return get_prompt(self.llm_type, PromptType.SEMANTIC_PARSING, query=query)


class SimilarQueryGenerator(BasePromptGenerator):
    def __init__(self, llm_type: LLMType):
        self.llm_type = llm_type

    def generate(self, query: str) -> str:
        return get_prompt(self.llm_type, PromptType.SIMILAR_QUERY, query=query)
