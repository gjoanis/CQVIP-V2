from app.knowledge.rag.semantic_search import semantic_search


class SearchService:
    """Thin façade over the RAG semantic search used by the Knowledge Library UI."""

    def search(self, query: str, *, collection: str = "knowledge_base", top_k: int = 10) -> list[dict]:
        return semantic_search(query, collection=collection, top_k=top_k)
