from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.report import Report
from app.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, db: Session):
        self.repo = ReportRepository(db)

    def list_for_project(self, project_id: str) -> list[Report]:
        return [r for r in self.repo.list_all(limit=1000) if r.project_id == project_id]

    def get(self, report_id: str) -> Report:
        return self.repo.get_or_404(report_id)

    def get_in_project(self, project_id: str, report_id: str) -> Report:
        """Fetches report_id but 404s unless it actually belongs to project_id --
        without this, a report_id from a *different* project the caller owns
        would be readable/downloadable/editable through this project's URL."""
        report = self.get(report_id)
        if report.project_id != project_id:
            raise NotFoundError("Report", report_id)
        return report

    def read_content(self, report: Report) -> str:
        with open(report.file_path) as f:
            return f.read()

    def write_content(self, report: Report, content: str) -> None:
        with open(report.file_path, "w") as f:
            f.write(content)

    def record_generated(self, **fields) -> Report:
        """Called by app/workflows + app/ai report generators once a file has been written to storage/."""
        return self.repo.create(Report(**fields))
