from sqlalchemy.orm import Session

from app.services.notification_service import NotificationService


def notify_user(db: Session, *, user_id: str, title: str, message: str = "",
                 notification_type: str = "info", link: str = "") -> None:
    """Fire-and-forget notification trigger, called from other workflow steps."""
    NotificationService(db).notify(
        user_id=user_id, title=title, message=message,
        notification_type=notification_type, link=link,
    )
