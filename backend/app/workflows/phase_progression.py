from sqlalchemy.orm import Session

from app.models.enums import PhaseStatus
from app.repositories.milestone_repository import MilestoneRepository
from app.repositories.phase_repository import PhaseRepository


def refresh_phase_status(db: Session, phase_id: str) -> None:
    """A phase completes once every milestone tied to it is complete."""
    phases = PhaseRepository(db)
    milestones = [m for m in MilestoneRepository(db).list_all(limit=1000) if m.phase_id == phase_id]
    if not milestones:
        return
    phase = phases.get_or_404(phase_id)
    if all(m.status == PhaseStatus.COMPLETE for m in milestones):
        phases.update(phase, status=PhaseStatus.COMPLETE)
    elif any(m.status == PhaseStatus.IN_PROGRESS for m in milestones):
        phases.update(phase, status=PhaseStatus.IN_PROGRESS)
