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
    metadatas = [{**metadata, "document_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
    collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def list_documents(collection_name: str) -> list[dict]:
    """Groups the chunks in a collection back into one row per source document,
    so the UI can show what's already been ingested instead of raw chunks."""
    collection = get_collection(collection_name)
    data = collection.get()
    by_doc: dict[str, dict] = {}
    for meta in data["metadatas"]:
        # Chunks ingested before document_id was stored in metadata (the original
        # one-off script run) fall back to a key derived from their title so they
        # still group correctly and show up here.
        doc_id = meta.get("document_id") or hashlib.sha1(meta.get("title", "").encode()).hexdigest()[:12]
        if doc_id not in by_doc:
            by_doc[doc_id] = {k: v for k, v in meta.items() if k != "chunk_index"}
            by_doc[doc_id]["document_id"] = doc_id
            by_doc[doc_id]["chunk_count"] = 0
        by_doc[doc_id]["chunk_count"] += 1
    return sorted(by_doc.values(), key=lambda d: d.get("added_at", ""), reverse=True)


def delete_document(collection_name: str, document_id: str) -> None:
    collection = get_collection(collection_name)
    collection.delete(where={"document_id": document_id})
