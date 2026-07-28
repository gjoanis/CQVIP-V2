from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin


class Evidence(Base, IDMixin, TimestampMixin):
    __tablename__ = "evidence"

    test_step_id: Mapped[Optional[str]] = mapped_column(ForeignKey("test_steps.id"), nullable=True)
    validation_activity_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("validation_activities.id"), nullable=True
    )
    uploaded_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str] = mapped_column(Text, default="")
