from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.enums import ApprovalStatus
from app.workflows.notifications import notify_user


class ApprovalWorkflow:
    """Generic approval flow for any entity_type/entity_id pair (documents, protocols, CAPAs, ...)."""

    def __init__(self, db: Session):
        self.db = db

    def submit(self, *, entity_type: str, entity_id: str, approver_id: str) -> Approval:
        approval = Approval(entity_type=entity_type, entity_id=entity_id, approver_id=approver_id)
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        notify_user(
            self.db, user_id=approver_id, title=f"Approval requested: {entity_type}",
            notification_type="approval_request",
        )
        return approval

    def decide(self, approval_id: str, *, status: ApprovalStatus, comments: str = "") -> Approval:
        approval = self.db.get(Approval, approval_id)
        approval.status = status
        approval.comments = comments
        approval.approved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(approval)
        return approval
