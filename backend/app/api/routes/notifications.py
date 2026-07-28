from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationOut(BaseModel):
    id: str
    title: str
    message: str
    is_read: bool
    link: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[NotificationOut])
def list_unread(user_id: str, db: Session = Depends(get_db)):
    return NotificationService(db).list_unread(user_id)


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: str, db: Session = Depends(get_db)):
    return NotificationService(db).mark_read(notification_id)
