from sqlalchemy.orm import Session

from app.models.milestone import Milestone
from app.repositories.milestone_repository import MilestoneRepository


class MilestoneService:
    def __init__(self, db: Session):
        self.repo = MilestoneRepository(db)

    def create(self, **fields) -> Milestone:
        return self.repo.create(Milestone(**fields))

    def complete(self, milestone_id: str, completed_date) -> Milestone:
        return self.repo.update(self.repo.get_or_404(milestone_id), completed_date=completed_date, status="complete")
