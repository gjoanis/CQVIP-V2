from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import DeviationSeverity


class Deviation(Base, IDMixin, TimestampMixin):
    __tablename__ = "deviations"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    validation_activity_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("validation_activities.id"), nullable=True
    )
    raised_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[DeviationSeverity] = mapped_column(default=DeviationSeverity.MINOR)
    status: Mapped[str] = mapped_column(String(50), default="open")
