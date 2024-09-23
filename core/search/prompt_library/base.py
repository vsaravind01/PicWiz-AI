from abc import ABC, abstractmethod
from core.search.prompt_library.types import LLMType


class BasePromptAdapter(ABC):
    def __init__(self, llm_type: LLMType):
        self.llm_type = llm_type

    @abstractmethod
    def generate_prompt(self, query: str) -> str:
        pass

    @abstractmethod
    async def execute_prompt(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def parse_response(self, response: str) -> dict:
        pass


class BasePromptGenerator(ABC):
    def __init__(self, llm_type: LLMType):
        self.llm_type = llm_type

    @abstractmethod
    def generate(self, query: str, **kwargs) -> str:
        pass
