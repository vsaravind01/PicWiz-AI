import os
from typing import Any

import cohere
from db import DB_CONNECTION_MAP
from models import User
from handlers import PhotoHandler, PersonHandler
from settings import Settings
from core.search.db_ops import DatabaseOperations, PeopleSearcher, PhotoSearcher
from core.search.search_plugin import search_plugin
from core.search.templates.semantic_parsing_template import SemanticParsingTemplate
from core.search.prompt_library import PromptFactory, AdapterType
from core.search.templates.clip_embedding_template import ClipEmbeddingTemplate

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")


class LLMSearch:

    def __init__(self, user: User, settings: Settings, adapter_type: AdapterType, model: str):
        self.user = user
        self.settings = settings
        self.cohere_client = cohere.Client(api_key=COHERE_API_KEY)

        db_ops = DatabaseOperations()
        db_ops.register_searcher(
            ["people"], PeopleSearcher(PersonHandler(DB_CONNECTION_MAP[settings.db.db_type]))
        )
        db_ops.register_searcher(
            ["objects", "locations"],
            PhotoSearcher(PhotoHandler(DB_CONNECTION_MAP[settings.db.db_type])),
        )

        adapter = PromptFactory.get_adapter(adapter_type, client=self.cohere_client, model=model)
        semantic_template = SemanticParsingTemplate(adapter, db_ops)
        clip_template = ClipEmbeddingTemplate(adapter, db_ops)
        search_plugin.register_template(semantic_template)
        search_plugin.register_template(clip_template)

    async def search(self, query: str, **kwargs) -> dict[str, Any]:
        results = {}
        for template in search_plugin.get_templates().values():
            result = await template.search(query, self.user, **kwargs)
            results[template.name] = result

        return results


async def llm_search(query: str, user: User, settings: Settings) -> dict[str, Any]:
    search = LLMSearch(user, settings, AdapterType.COHERE, "command-r")
    return await search.search(query)
