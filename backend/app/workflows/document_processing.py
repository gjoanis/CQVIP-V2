from sqlalchemy.orm import Session

from app.ai.requirement_extraction import RequirementExtraction
from app.models.document import Document
from app.models.requirement import Requirement
from app.parsers.factory import ParserFactory
from app.repositories.requirement_repository import RequirementRepository
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
    """Runs after a Document row is created: parse it, and for spec-type
    documents (URS/FS/DS/HDS/SDS) extract requirements via Claude and persist
    them as Requirement rows linked back to this document.
    """
    parser = ParserFactory.for_file(document.file_path, doc_type=document.doc_type)
    try:
        parsed = parser.parse(document.file_path)
        details = {"sections": len(parsed.sections)}

        if document.doc_type.upper() in SPEC_DOC_TYPES:
            extracted = RequirementExtraction().run(parsed.raw_text)
            requirements = RequirementRepository(db)
            for i, item in enumerate(extracted, start=1):
                req_code = _clean_req_code(item.get("req_code")) or f"{document.doc_type.upper()}-{i:03d}"
                title = item.get("title") or item.get("description", "")[:255] or req_code
                requirements.create(Requirement(
                    project_id=document.project_id,
                    document_id=document.id,
                    system_id=document.system_id,
                    req_code=req_code,
                    title=title,
                    description=item.get("description", ""),
                    category=item.get("category", ""),
                    source=document.name,
                ))
            details["requirements_extracted"] = len(extracted)
    except Exception as exc:  # noqa: BLE001 - surfaced via audit log, not raised
        details = {"error": str(exc)}
    log_action(
        db, user_id=document.uploaded_by_id, action="parse_document",
        entity_type="Document", entity_id=document.id, details=details,
    )
