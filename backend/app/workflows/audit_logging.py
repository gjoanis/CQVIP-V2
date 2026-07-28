from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(db: Session, *, user_id: str | None, action: str, entity_type: str,
                entity_id: str, details: dict | None = None) -> AuditLog:
    entry = AuditLog(
        user_id=user_id, action=action, entity_type=entity_type,
        entity_id=entity_id, details=details or {},
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
