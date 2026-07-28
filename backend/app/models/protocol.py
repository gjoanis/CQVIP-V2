from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import ApprovalStatus


class Protocol(Base, IDMixin, TimestampMixin):
    __tablename__ = "protocols"

    validation_activity_id: Mapped[str] = mapped_column(ForeignKey("validation_activities.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    protocol_number: Mapped[str] = mapped_column(String(50), unique=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    status: Mapped[ApprovalStatus] = mapped_column(default=ApprovalStatus.PENDING)
    file_path: Mapped[str] = mapped_column(String(1000), default="")

    validation_activity: Mapped["ValidationActivity"] = relationship(back_populates="protocols")
    test_steps: Mapped[list["TestStep"]] = relationship(back_populates="protocol", cascade="all, delete-orphan")
