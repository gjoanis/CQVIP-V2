import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.models.requirement import Requirement
from app.models.requirement_relationship import RequirementRelationship
from app.models.risk import Risk
from app.models.traceability import Traceability
from app.repositories.requirement_repository import RequirementRepository


class RequirementService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RequirementRepository(db)

    def get(self, requirement_id: str) -> Requirement:
        return self.repo.get_or_404(requirement_id)

    def list_for_project(self, project_id: str) -> list[Requirement]:
        return self.repo.list_for_project(project_id)

    def create(self, **fields) -> Requirement:
        return self.repo.create(Requirement(**fields))

    def update(self, requirement_id: str, **fields) -> Requirement:
        return self.repo.update(self.get(requirement_id), **fields)

    def delete_for_document(self, document_id: str) -> int:
        """Deletes every requirement extracted from a document, so re-uploading
        and re-extracting that document starts from a truly clean slate."""
        ids = list(
            self.db.execute(select(Requirement.id).where(Requirement.document_id == document_id)).scalars()
        )
        for requirement_id in ids:
            self.delete(requirement_id)
        return len(ids)

    def delete_for_project(self, project_id: str) -> int:
        """Deletes every requirement in a project, used by project reset."""
        ids = list(self.db.execute(select(Requirement.id).where(Requirement.project_id == project_id)).scalars())
        for requirement_id in ids:
            self.delete(requirement_id)
        return len(ids)

    def delete(self, requirement_id: str) -> None:
        """Deleting a requirement with live traceability links, requirement
        relationships, or linked risks would violate their foreign keys on
        Postgres, so those dependents are cleaned up first: traceability
        links and relationships are meaningless without the requirement and
        are deleted, while risks are project-level entities that can outlive
        the requirement and just get unlinked."""
        requirement = self.get(requirement_id)
        for link in self.db.execute(
            select(Traceability).where(Traceability.requirement_id == requirement_id)
        ).scalars():
            self.db.delete(link)
        for rel in self.db.execute(
            select(RequirementRelationship).where(
                (RequirementRelationship.source_requirement_id == requirement_id)
                | (RequirementRelationship.target_requirement_id == requirement_id)
            )
        ).scalars():
            self.db.delete(rel)
        for risk in self.db.execute(select(Risk).where(Risk.requirement_id == requirement_id)).scalars():
            risk.requirement_id = None
        for attachment in self.db.execute(
            select(Attachment).where(Attachment.entity_type == "Requirement", Attachment.entity_id == requirement_id)
        ).scalars():
            if attachment.file_path and os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)
            self.db.delete(attachment)
        self.db.commit()
        self.repo.delete(requirement)
