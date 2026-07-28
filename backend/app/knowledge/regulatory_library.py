"""Catalog of regulatory bodies whose documents live in the 'regulatory' RAG collection.

This is metadata, not the documents themselves -- actual content is ingested via
app.knowledge.rag.chunk_index.index_document() and tagged with one of these codes.
"""
from app.knowledge.rag.chunk_index import index_document

REGULATORY_BODIES = [
    "FDA", "EMA", "MHRA", "Health Canada", "WHO", "PIC/S", "TGA", "PMDA", "ANVISA", "ICH",
]

COLLECTION = "regulatory_library"


def ingest(body: str, title: str, text: str, source_url: str = "") -> int:
    if body not in REGULATORY_BODIES:
        raise ValueError(f"Unknown regulatory body: {body}")
    return index_document(
        COLLECTION, text, metadata={"body": body, "title": title, "source_url": source_url},
    )
