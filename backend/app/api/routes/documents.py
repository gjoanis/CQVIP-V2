from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_document_owner, require_project_owner
from app.config import get_settings
from app.services.document_service import DocumentService
from app.workflows.document_processing import extract_requirements_from_document

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


class DocumentOut(BaseModel):
    id: str
    project_id: str
    system_id: str | None
    name: str
    doc_type: str
    version: str
    status: str
    file_path: str

    model_config = {"from_attributes": True}


class ExtractedRequirementOut(BaseModel):
    req_code: str
    title: str
    description: str
    category: str


@router.get("", response_model=list[DocumentOut])
def list_documents(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    return DocumentService(db).list_for_project(project_id)


@router.post("", response_model=DocumentOut)
async def upload_document(
    doc_type: str, file: UploadFile, project_id: str = Depends(require_project_owner),
    system_id: str | None = None, db: Session = Depends(get_db),
):
    import os

    dest_dir = os.path.join(settings.storage_root, "uploads", project_id)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)
    with open(dest_path, "wb") as out:
        out.write(await file.read())
    return DocumentService(db).upload(
        project_id=project_id, name=file.filename, doc_type=doc_type, file_path=dest_path,
        system_id=system_id,
    )


@router.delete("/{document_id}")
def delete_document(document_id: str = Depends(require_document_owner), db: Session = Depends(get_db)):
    deleted_requirements = DocumentService(db).delete(document_id)
    return {"deleted": document_id, "deleted_requirements": deleted_requirements}


@router.post("/{document_id}/extract-requirements", response_model=list[ExtractedRequirementOut])
def extract_requirements(document_id: str = Depends(require_document_owner), db: Session = Depends(get_db)):
    """Parses the document and returns AI-extracted candidate requirements for
    review -- nothing is persisted here. The frontend creates a Requirement
    row (via the existing POST /requirements) for each one the user accepts."""
    document = DocumentService(db).get(document_id)
    try:
        return extract_requirements_from_document(db, document)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
