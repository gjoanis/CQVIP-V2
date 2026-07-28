from sqlalchemy.orm import Session

from app.models.milestone import Milestone
from app.repositories.milestone_repository import MilestoneRepository
from app.repositories.phase_repository import PhaseRepository


class ScheduleService:
    """Aggregate view over phases + milestones for a project timeline."""

    def __init__(self, db: Session):
        self.phases = PhaseRepository(db)
        self.milestones = MilestoneRepository(db)

    def timeline_for_project(self, project_id: str) -> dict:
        phases = [p for p in self.phases.list_all(limit=1000) if p.project_id == project_id]
        milestones = [m for m in self.milestones.list_all(limit=1000) if m.project_id == project_id]
        return {"phases": phases, "milestones": milestones}
