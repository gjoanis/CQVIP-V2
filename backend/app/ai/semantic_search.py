from app.ai.base import AICapability
from app.knowledge.rag.semantic_search import semantic_search


class SemanticSearch(AICapability):
    """AI-layer façade over the RAG semantic search implemented in app.knowledge.rag."""

    def run(self, query: str, *, collection: str = "knowledge_base", top_k: int = 10) -> list[dict]:
        return semantic_search(query, collection=collection, top_k=top_k)
