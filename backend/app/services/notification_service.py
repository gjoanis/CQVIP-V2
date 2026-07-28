from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def notify(self, *, user_id: str, title: str, message: str = "", notification_type="info",
                link: str = "") -> Notification:
        return self.repo.create(Notification(
            user_id=user_id, title=title, message=message,
            notification_type=notification_type, link=link,
        ))

    def list_unread(self, user_id: str) -> list[Notification]:
        return self.repo.list_unread(user_id)

    def mark_read(self, notification_id: str) -> Notification:
        return self.repo.update(self.repo.get_or_404(notification_id), is_read=True)
