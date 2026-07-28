from app.knowledge.rag.chroma_client import get_collection
from app.knowledge.rag.citations import citations_from_query_result


def semantic_search(query: str, *, collection: str = "knowledge_base", top_k: int = 10) -> list[dict]:
    coll = get_collection(collection)
    if coll.count() == 0:
        return []
    result = coll.query(query_texts=[query], n_results=min(top_k, coll.count()))
    citations = citations_from_query_result(result)
    return [
        {"text": c.text, "source": c.source_label, "metadata": c.metadata, "distance": c.distance}
        for c in citations
    ]
