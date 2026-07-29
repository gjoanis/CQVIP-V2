import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile

from app.config import get_settings
from app.knowledge import client_knowledge, industry_standards, internal_knowledge, regulatory_library
from app.knowledge.rag.chunk_index import delete_document, index_document, list_documents
from app.parsers.factory import ParserFactory
from app.services.search_service import SearchService

router = APIRouter(prefix="/knowledge", tags=["knowledge-library"])
settings = get_settings()

# Each collection tags its chunks with a different taxonomy field (the thing
# a searcher would filter/browse by), drawn from the fixed vocab already
# defined alongside each collection's (unused-until-now) ingest() helper.
COLLECTION_TAXONOMY = {
    regulatory_library.COLLECTION: {"field": "body", "values": regulatory_library.REGULATORY_BODIES},
    industry_standards.COLLECTION: {"field": "standard", "values": industry_standards.STANDARDS_BODIES},
    client_knowledge.COLLECTION: {"field": "category", "values": client_knowledge.CLIENT_KNOWLEDGE_CATEGORIES},
    internal_knowledge.COLLECTION: {"field": "category", "values": internal_knowledge.INTERNAL_KNOWLEDGE_CATEGORIES},
}


@router.get("/search")
def search_knowledge(q: str, collection: str = "knowledge_base", top_k: int = 10):
    return SearchService().search(q, collection=collection, top_k=top_k)


@router.get("/taxonomy")
def get_taxonomy():
    return {name: cfg["values"] for name, cfg in COLLECTION_TAXONOMY.items()}


@router.get("/documents")
def get_documents(collection: str):
    if collection not in COLLECTION_TAXONOMY:
        raise HTTPException(400, f"Unknown collection: {collection}")
    return list_documents(collection)


@router.post("/documents")
async def upload_document(
    collection: str,
    title: str,
    taxonomy_value: str,
    file: UploadFile,
    source_url: str = "",
    client_id: str | None = None,
    uploaded_by_id: str | None = None,
):
    if collection not in COLLECTION_TAXONOMY:
        raise HTTPException(400, f"Unknown collection: {collection}")
    taxonomy = COLLECTION_TAXONOMY[collection]
    if taxonomy_value not in taxonomy["values"]:
        raise HTTPException(400, f"'{taxonomy_value}' is not a valid {taxonomy['field']} for {collection}")
    if collection == client_knowledge.COLLECTION and not client_id:
        raise HTTPException(400, "client_id is required for client_knowledge uploads")

    dest_dir = os.path.join(settings.storage_root, "knowledge_uploads", collection)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)
    with open(dest_path, "wb") as out:
        out.write(await file.read())

    parser = ParserFactory.for_file(dest_path)
    parsed = parser.parse(dest_path)

    document_id = uuid.uuid4().hex[:12]
    metadata = {
        "document_id": document_id,
        "title": title,
        "source_url": source_url or file.filename,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by_id": uploaded_by_id or "",
        taxonomy["field"]: taxonomy_value,
    }
    if collection == client_knowledge.COLLECTION:
        metadata["client_id"] = client_id

    chunk_count = index_document(collection, parsed.raw_text, metadata)
    return {"document_id": document_id, "chunk_count": chunk_count, **metadata}


@router.delete("/documents/{document_id}")
def remove_document(document_id: str, collection: str):
    if collection not in COLLECTION_TAXONOMY:
        raise HTTPException(400, f"Unknown collection: {collection}")
    delete_document(collection, document_id)
    return {"deleted": document_id}
