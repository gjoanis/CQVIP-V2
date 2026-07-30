from sqlalchemy.orm import Session

from app.ai.requirement_extraction import RequirementExtraction
from app.models.document import Document
from app.parsers.factory import ParserFactory
from app.workflows.audit_logging import log_action

# Doc types worth running requirement extraction on. Test/execution records
# (FAT, SAT, IQ, OQ, PQ, ...) don't contain requirements to extract.
SPEC_DOC_TYPES = {"URS", "FS", "DS", "HDS", "SDS"}

# Models asked to omit req_code when the source has none sometimes return a
# placeholder string instead -- treat those the same as "not provided".
_PLACEHOLDER_VALUES = {"n/a", "na", "none", "unknown", "-", ""}


def _clean_req_code(value: str | None) -> str | None:
    if value is None or value.strip().lower() in _PLACEHOLDER_VALUES:
        return None
    return value.strip()


def process_uploaded_document(db: Session, document: Document) -> None:
    """Runs after a Document row is created. Requirement extraction is a
    separate, on-demand step (extract_requirements_from_document below) so an
    engineer reviews AI-extracted requirements before they become official
    records -- this just records the upload in the audit trail.
    """
    log_action(
        db, user_id=document.uploaded_by_id, action="upload_document",
        entity_type="Document", entity_id=document.id,
    )


def extract_requirements_from_document(db: Session, document: Document) -> list[dict]:
    """Parses the document and runs AI requirement extraction, returning
    candidate requirements for review -- does NOT persist anything. The
    caller (the frontend, via POST /requirements per accepted candidate)
    decides what actually becomes a Requirement row.
    """
    if document.doc_type.upper() not in SPEC_DOC_TYPES:
        raise ValueError(f"Requirement extraction isn't applicable to {document.doc_type} documents")

    parser = ParserFactory.for_file(document.file_path, doc_type=document.doc_type)
    parsed = parser.parse(document.file_path)
    extracted = RequirementExtraction().run(parsed.raw_text)

    candidates = []
    for i, item in enumerate(extracted, start=1):
        req_code = _clean_req_code(item.get("req_code")) or f"{document.doc_type.upper()}-{i:03d}"
        title = item.get("title") or item.get("description", "")[:255] or req_code
        candidates.append({
            "req_code": req_code, "title": title,
            "description": item.get("description", ""), "category": item.get("category", ""),
        })

    log_action(
        db, user_id=document.uploaded_by_id, action="extract_requirements",
        entity_type="Document", entity_id=document.id, details={"candidates_found": len(candidates)},
    )
    return candidates
