from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import ApprovalStatus


class Approval(Base, IDMixin, TimestampMixin):
    """Polymorphic approval: entity_type + entity_id point at the record being approved."""

    __tablename__ = "approvals"

    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    approver_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ApprovalStatus] = mapped_column(default=ApprovalStatus.PENDING)
    comments: Mapped[str] = mapped_column(Text, default="")
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
