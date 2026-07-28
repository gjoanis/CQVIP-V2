from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import get_settings
from app.services.document_service import DocumentService

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


@router.get("", response_model=list[DocumentOut])
def list_documents(project_id: str, db: Session = Depends(get_db)):
    return DocumentService(db).list_for_project(project_id)


@router.post("", response_model=DocumentOut)
async def upload_document(
    project_id: str, doc_type: str, file: UploadFile,
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
