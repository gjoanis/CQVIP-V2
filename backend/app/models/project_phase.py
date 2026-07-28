from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import PhaseStatus


class ProjectPhase(Base, IDMixin, TimestampMixin):
    __tablename__ = "project_phases"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[PhaseStatus] = mapped_column(default=PhaseStatus.NOT_STARTED)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="phases")
