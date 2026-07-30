from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.models.enums import ValidationActivityType
from app.models.project import Project
from app.models.validation_activity import ValidationActivity
from app.repositories.validation_repository import ValidationRepository

# The standard commissioning & qualification lifecycle, in execution order --
# used to seed a project's timeline with the phases it should be tracking.
STANDARD_PHASES: list[tuple[ValidationActivityType, str]] = [
    (ValidationActivityType.ENGINEERING_STUDY, "Engineering Studies"),
    (ValidationActivityType.FAT, "Factory Acceptance Testing (FAT)"),
    (ValidationActivityType.SAT, "Site Acceptance Testing (SAT)"),
    (ValidationActivityType.COMMISSIONING, "Commissioning"),
    (ValidationActivityType.IQ, "Installation Qualification (IQ)"),
    (ValidationActivityType.OQ, "Operational Qualification (OQ)"),
    (ValidationActivityType.PQ, "Performance Qualification (PQ)"),
    (ValidationActivityType.FINAL_REPORT, "Final Validation Report"),
]


class ValidationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ValidationRepository(db)

    def _check_within_project_window(self, project_id: str, **dates: date | None) -> None:
        """Every validation activity has to execute within its project's overall
        timeframe (Project.start_date -> Project.target_end_date). If the project
        hasn't set a timeframe yet, there's nothing to enforce."""
        project = self.db.get(Project, project_id)
        if project is None or (project.start_date is None and project.target_end_date is None):
            return
        for label, value in dates.items():
            if value is None:
                continue
            field_name = label.replace("_", " ")
            if project.start_date and value < project.start_date:
                raise ValidationError(
                    f"{field_name} ({value.isoformat()}) is before the project's start date "
                    f"({project.start_date.isoformat()})."
                )
            if project.target_end_date and value > project.target_end_date:
                raise ValidationError(
                    f"{field_name} ({value.isoformat()}) is after the project's target end date "
                    f"({project.target_end_date.isoformat()})."
                )

    def list_for_project(self, project_id: str) -> list[ValidationActivity]:
        return [v for v in self.repo.list_all(limit=1000) if v.project_id == project_id]

    def create(self, **fields) -> ValidationActivity:
        self._check_within_project_window(
            fields["project_id"],
            planned_date=fields.get("planned_date"),
            start_date=fields.get("start_date"),
            end_date=fields.get("end_date"),
        )
        return self.repo.create(ValidationActivity(**fields))

    def update(self, activity_id: str, **fields) -> ValidationActivity:
        activity = self.repo.get_or_404(activity_id)
        self._check_within_project_window(
            activity.project_id,
            planned_date=fields.get("planned_date"),
            start_date=fields.get("start_date"),
            end_date=fields.get("end_date"),
        )
        return self.repo.update(activity, **fields)

    def record_result(self, activity_id: str, status: str, actual_date) -> ValidationActivity:
        return self.repo.update(self.repo.get_or_404(activity_id), status=status, actual_date=actual_date)

    def delete(self, activity_id: str) -> None:
        self.repo.delete(self.repo.get_or_404(activity_id))

    def seed_standard_phases(self, project_id: str) -> list[ValidationActivity]:
        """Creates any of the 8 standard C&Q phases not already tracked for
        this project, so the timeline has every phase to plot from the start."""
        existing_types = {v.activity_type for v in self.list_for_project(project_id)}
        created = []
        for activity_type, label in STANDARD_PHASES:
            if activity_type in existing_types:
                continue
            created.append(self.create(project_id=project_id, name=label, activity_type=activity_type))
        return created
