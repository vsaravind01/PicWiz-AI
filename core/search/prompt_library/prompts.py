from core.search.prompt_library.types import LLMType, PromptType
from core.search.prompt_library.prompt_collections import cohere_prompt

PROMPTS: dict[LLMType, dict[PromptType, str]] = {
    LLMType.COHERE: {
        PromptType.SEMANTIC_PARSING: cohere_prompt.SEMANTIC_PARSING,
        PromptType.SIMILAR_QUERY: cohere_prompt.SIMILAR_QUERY,
    },
}


def get_prompt(llm: LLMType, prompt_type: PromptType, **kwargs) -> str:
    prompt = PROMPTS[llm][prompt_type]
    return prompt.format(**kwargs)
