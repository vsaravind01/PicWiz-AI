from fastapi import APIRouter, Depends

from core.search.llm_search import CohereSearch
from routers.dependencies.auth_jwt import get_current_user


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/q/{query}")
async def search(query: str, user=Depends(get_current_user)):
    search = CohereSearch(user=user)
    return search.search(query)
