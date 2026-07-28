from app.knowledge.rag.chunk_index import index_document

CLIENT_KNOWLEDGE_CATEGORIES = [
    "Client SOPs", "Validation Standards", "Engineering Standards", "Specifications",
    "Templates", "Lessons Learned", "Historical Projects",
]

COLLECTION = "client_knowledge"


def ingest(client_id: str, category: str, title: str, text: str) -> int:
    if category not in CLIENT_KNOWLEDGE_CATEGORIES:
        raise ValueError(f"Unknown client knowledge category: {category}")
    return index_document(
        COLLECTION, text, metadata={"client_id": client_id, "category": category, "title": title},
    )
