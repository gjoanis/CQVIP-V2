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


def _finalize_upload(
    *, collection: str, title: str, taxonomy_value: str, dest_path: str, filename: str,
    source_url: str, client_id: str | None, uploaded_by_id: str | None,
) -> dict:
    """Shared by both the direct single-request upload and the chunked-upload
    completion step: validates the taxonomy, parses the file already sitting
    at dest_path, and indexes it into the RAG collection."""
    if collection not in COLLECTION_TAXONOMY:
        raise HTTPException(400, f"Unknown collection: {collection}")
    taxonomy = COLLECTION_TAXONOMY[collection]
    if taxonomy_value not in taxonomy["values"]:
        raise HTTPException(400, f"'{taxonomy_value}' is not a valid {taxonomy['field']} for {collection}")
    if collection == client_knowledge.COLLECTION and not client_id:
        raise HTTPException(400, "client_id is required for client_knowledge uploads")

    parser = ParserFactory.for_file(dest_path)
    parsed = parser.parse(dest_path)

    document_id = uuid.uuid4().hex[:12]
    metadata = {
        "document_id": document_id,
        "title": title,
        "source_url": source_url or filename,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by_id": uploaded_by_id or "",
        taxonomy["field"]: taxonomy_value,
    }
    if collection == client_knowledge.COLLECTION:
        metadata["client_id"] = client_id

    chunk_count = index_document(collection, parsed.raw_text, metadata)
    return {"document_id": document_id, "chunk_count": chunk_count, **metadata}


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

    dest_dir = os.path.join(settings.storage_root, "knowledge_uploads", collection)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)
    with open(dest_path, "wb") as out:
        out.write(await file.read())

    return _finalize_upload(
        collection=collection, title=title, taxonomy_value=taxonomy_value, dest_path=dest_path,
        filename=file.filename, source_url=source_url, client_id=client_id, uploaded_by_id=uploaded_by_id,
    )


@router.post("/documents/upload-chunk")
async def upload_chunk(upload_id: str, chunk_index: int, chunk: UploadFile):
    """One piece of a large file, sent as its own small request. Large single
    uploads are fragile to any transient network blip during their (multi-
    second) transfer -- breaking the file into many small, fast requests
    means a dropped connection only costs one chunk, which the client can
    just retry, instead of the whole file."""
    tmp_dir = os.path.join(settings.storage_root, "knowledge_uploads", "_chunks", upload_id)
    os.makedirs(tmp_dir, exist_ok=True)
    chunk_path = os.path.join(tmp_dir, f"{chunk_index:06d}")
    with open(chunk_path, "wb") as out:
        out.write(await chunk.read())
    return {"received": chunk_index}


@router.post("/documents/complete-chunked-upload")
def complete_chunked_upload(
    upload_id: str,
    filename: str,
    total_chunks: int,
    collection: str,
    title: str,
    taxonomy_value: str,
    source_url: str = "",
    client_id: str | None = None,
    uploaded_by_id: str | None = None,
):
    tmp_dir = os.path.join(settings.storage_root, "knowledge_uploads", "_chunks", upload_id)
    chunk_paths = [os.path.join(tmp_dir, f"{i:06d}") for i in range(total_chunks)]
    missing = [i for i, p in enumerate(chunk_paths) if not os.path.exists(p)]
    if missing:
        raise HTTPException(400, f"Missing chunk(s) {missing} -- re-upload them before completing.")

    if collection not in COLLECTION_TAXONOMY:
        raise HTTPException(400, f"Unknown collection: {collection}")
    dest_dir = os.path.join(settings.storage_root, "knowledge_uploads", collection)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, "wb") as out:
        for chunk_path in chunk_paths:
            with open(chunk_path, "rb") as chunk_file:
                out.write(chunk_file.read())

    for chunk_path in chunk_paths:
        os.remove(chunk_path)
    os.rmdir(tmp_dir)

    return _finalize_upload(
        collection=collection, title=title, taxonomy_value=taxonomy_value, dest_path=dest_path,
        filename=filename, source_url=source_url, client_id=client_id, uploaded_by_id=uploaded_by_id,
    )


@router.delete("/documents/{document_id}")
def remove_document(document_id: str, collection: str):
    if collection not in COLLECTION_TAXONOMY:
        raise HTTPException(400, f"Unknown collection: {collection}")
    delete_document(collection, document_id)
    return {"deleted": document_id}
