from sqlalchemy.orm import Session

from app.models.report import Report
from app.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, db: Session):
        self.repo = ReportRepository(db)

    def list_for_project(self, project_id: str) -> list[Report]:
        return [r for r in self.repo.list_all(limit=1000) if r.project_id == project_id]

    def get(self, report_id: str) -> Report:
        return self.repo.get_or_404(report_id)

    def record_generated(self, **fields) -> Report:
        """Called by app/workflows + app/ai report generators once a file has been written to storage/."""
        return self.repo.create(Report(**fields))
