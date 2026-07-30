from sqlalchemy import select
from sqlalchemy.orm import Session

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
        self.db.commit()
        self.repo.delete(requirement)
