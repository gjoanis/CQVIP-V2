from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.deadline import Deadline
from app.repositories.deadline_repository import DeadlineRepository


class DeadlineService:
    def __init__(self, db: Session):
        self.repo = DeadlineRepository(db)

    def create(self, **fields) -> Deadline:
        return self.repo.create(Deadline(**fields))

    def upcoming(self, within_days: int = 7) -> list[Deadline]:
        horizon = date.today() + timedelta(days=within_days)
        return [d for d in self.repo.list_all(limit=1000) if d.due_date <= horizon and d.status != "complete"]
