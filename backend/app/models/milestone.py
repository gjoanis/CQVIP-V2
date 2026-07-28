from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import PhaseStatus


class Milestone(Base, IDMixin, TimestampMixin):
    __tablename__ = "milestones"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    phase_id: Mapped[Optional[str]] = mapped_column(ForeignKey("project_phases.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[PhaseStatus] = mapped_column(default=PhaseStatus.NOT_STARTED)
