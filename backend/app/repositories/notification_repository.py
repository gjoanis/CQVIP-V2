from sqlalchemy import select
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    def list_unread(self, user_id: str):
        stmt = select(self.model).where(
            self.model.user_id == user_id, self.model.is_read.is_(False)
        )
        return list(self.db.execute(stmt).scalars().all())
