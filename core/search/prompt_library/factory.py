from typing import Dict, Type
from core.search.prompt_library.base import BasePromptAdapter, BasePromptGenerator
from core.search.prompt_library.adapters import CohereAdapter
from core.search.prompt_library.generators import SemanticParsingGenerator, SimilarQueryGenerator
from core.search.prompt_library.types import AdapterType, GeneratorType, LLMType


class PromptFactory:
    _adapters: Dict[AdapterType, Type[BasePromptAdapter]] = {
        AdapterType.COHERE: CohereAdapter,
    }
    _generators: Dict[GeneratorType, Type[BasePromptGenerator]] = {
        GeneratorType.SEMANTIC_PARSING: SemanticParsingGenerator,
        GeneratorType.SIMILAR_QUERY: SimilarQueryGenerator,
    }

    @classmethod
    def get_adapter(cls, adapter_type: AdapterType, **kwargs) -> BasePromptAdapter:
        adapter_class = cls._adapters.get(adapter_type)
        if not adapter_class:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")
        return adapter_class(**kwargs)

    @classmethod
    def get_generator(cls, generator_type: GeneratorType, llm: LLMType) -> BasePromptGenerator:
        generator_class = cls._generators.get(generator_type)
        if not generator_class:
            raise ValueError(f"Unsupported generator type: {generator_type}")
        return generator_class(llm)
