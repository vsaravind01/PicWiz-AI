from fastapi import APIRouter, Depends

from core.search.llm_search import LLMSearch
from core.search.prompt_library.types import AdapterType
from routers.dependencies.auth_jwt import get_current_user
from settings import Settings


router = APIRouter(prefix="/search", tags=["search"])
settings = Settings()

@router.get("/q/{query}")
async def search(query: str, user=Depends(get_current_user)):
    llm_search = LLMSearch(
        user=user, settings=settings, adapter_type=AdapterType.COHERE, model="command-r"
    )
    result = await llm_search.search(query, k=5)
    return result
