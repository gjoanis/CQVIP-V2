from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories.deadline_repository import DeadlineRepository
from app.workflows.notifications import notify_user


def notify_upcoming_deadlines(db: Session, *, within_days: int = 3) -> int:
    """Intended to be invoked by app.workflows.background_jobs on a schedule."""
    horizon = date.today() + timedelta(days=within_days)
    deadlines = DeadlineRepository(db).list_all(limit=1000)
    due = [d for d in deadlines if d.status != "complete" and d.due_date <= horizon]
    for deadline in due:
        if deadline.owner_id:
            notify_user(
                db, user_id=deadline.owner_id, title=f"Deadline approaching: {deadline.title}",
                notification_type="deadline",
            )
    return len(due)
