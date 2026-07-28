from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.workflows.document_processing import process_uploaded_document


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)

    def get(self, document_id: str) -> Document:
        return self.repo.get_or_404(document_id)

    def list_for_project(self, project_id: str) -> list[Document]:
        return [d for d in self.repo.list_all(limit=1000) if d.project_id == project_id]

    def upload(self, *, project_id: str, name: str, doc_type: str, file_path: str,
                uploaded_by_id: str | None = None, system_id: str | None = None) -> Document:
        document = self.repo.create(Document(
            project_id=project_id, name=name, doc_type=doc_type,
            file_path=file_path, uploaded_by_id=uploaded_by_id, system_id=system_id,
        ))
        process_uploaded_document(self.db, document)
        return document
