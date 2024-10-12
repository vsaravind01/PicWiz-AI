from enum import Enum
from typing import Dict, Any

from matplotlib.style import available


class PromptType(Enum):
    SEMANTIC_PARSING = "semantic_parsing"
    SIMILAR_QUERY = "similar_query"


class AdapterType(Enum):
    COHERE = "cohere"


class GeneratorType(Enum):
    SEMANTIC_PARSING = "semantic_parsing"
    SIMILAR_QUERY = "similar_query"


class LLMType(Enum):
    COHERE = "cohere"

    @property
    def available_models(self) -> Dict[GeneratorType, list[str]]:
        map = {
            self.COHERE: {
                GeneratorType.SEMANTIC_PARSING: ["command-r"],
                GeneratorType.SIMILAR_QUERY: ["command-r"],
            }
        }
        return map[self]


PromptResult = Dict[str, Any]
