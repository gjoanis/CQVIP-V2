from fastapi import APIRouter

from app.services.search_service import SearchService

router = APIRouter(prefix="/knowledge", tags=["knowledge-library"])


@router.get("/search")
def search_knowledge(q: str, collection: str = "knowledge_base", top_k: int = 10):
    return SearchService().search(q, collection=collection, top_k=top_k)
