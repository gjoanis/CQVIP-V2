"""One-off migration: chunks ingested before document_id was part of the stored
metadata (the original regulatory PDF ingestion) get a document_id patched in,
derived from their title -- matching the same fallback list_documents() uses,
so both listing and deleting behave consistently for old and new documents.

Run from backend/ with the .venv312 interpreter:
    .venv312/bin/python scripts/backfill_document_ids.py
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.knowledge.rag.chroma_client import get_collection

COLLECTIONS = ["regulatory_library", "industry_standards", "client_knowledge", "internal_knowledge"]


def main() -> None:
    for name in COLLECTIONS:
        collection = get_collection(name)
        data = collection.get()
        ids_to_update, metadatas_to_update = [], []
        for chunk_id, meta in zip(data["ids"], data["metadatas"]):
            if meta.get("document_id"):
                continue
            doc_id = hashlib.sha1(meta.get("title", "").encode()).hexdigest()[:12]
            ids_to_update.append(chunk_id)
            metadatas_to_update.append({**meta, "document_id": doc_id})
        if ids_to_update:
            collection.update(ids=ids_to_update, metadatas=metadatas_to_update)
        print(f"{name}: patched {len(ids_to_update)} chunk(s)")


if __name__ == "__main__":
    main()
