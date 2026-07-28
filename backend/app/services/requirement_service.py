from sqlalchemy.orm import Session

from app.models.requirement import Requirement
from app.repositories.requirement_repository import RequirementRepository


class RequirementService:
    def __init__(self, db: Session):
        self.repo = RequirementRepository(db)

    def get(self, requirement_id: str) -> Requirement:
        return self.repo.get_or_404(requirement_id)

    def list_for_project(self, project_id: str) -> list[Requirement]:
        return self.repo.list_for_project(project_id)

    def create(self, **fields) -> Requirement:
        return self.repo.create(Requirement(**fields))

    def update(self, requirement_id: str, **fields) -> Requirement:
        return self.repo.update(self.get(requirement_id), **fields)
