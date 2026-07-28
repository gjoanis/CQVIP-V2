import hashlib
import uuid

from app.knowledge.rag.chroma_client import get_collection

DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 200


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE,
                overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap if end - overlap > start else end
    return chunks


def index_document(collection_name: str, text: str, metadata: dict) -> int:
    """Chunks a document and upserts it into the named Chroma collection. Returns chunk count."""
    collection = get_collection(collection_name)
    chunks = chunk_text(text)
    if not chunks:
        return 0
    doc_id = metadata.get("document_id") or hashlib.sha1(text.encode()).hexdigest()[:12]
    ids = [f"{doc_id}-{i}-{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
    metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]
    collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)
