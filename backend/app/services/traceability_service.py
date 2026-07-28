from sqlalchemy.orm import Session

from app.models.traceability import Traceability
from app.repositories.traceability_repository import TraceabilityRepository


class TraceabilityService:
    def __init__(self, db: Session):
        self.repo = TraceabilityRepository(db)

    def link(self, **fields) -> Traceability:
        return self.repo.create(Traceability(**fields))

    def matrix_for_project(self, project_id: str) -> list[Traceability]:
        return [t for t in self.repo.list_all(limit=5000) if t.project_id == project_id]

    def coverage_summary(self, project_id: str) -> dict:
        links = self.matrix_for_project(project_id)
        total = len(links)
        covered = sum(1 for link in links if link.coverage_status == "covered")
        return {"total": total, "covered": covered, "uncovered": total - covered}
