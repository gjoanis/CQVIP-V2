from app.knowledge.rag.chunk_index import index_document

INTERNAL_KNOWLEDGE_CATEGORIES = [
    "Company SOPs", "Validation Templates", "Best Practices", "Training Material", "Internal Guidance",
]

COLLECTION = "internal_knowledge"


def ingest(category: str, title: str, text: str) -> int:
    if category not in INTERNAL_KNOWLEDGE_CATEGORIES:
        raise ValueError(f"Unknown internal knowledge category: {category}")
    return index_document(COLLECTION, text, metadata={"category": category, "title": title})
