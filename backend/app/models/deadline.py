from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin


class Deadline(Base, IDMixin, TimestampMixin):
    __tablename__ = "deadlines"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    milestone_id: Mapped[Optional[str]] = mapped_column(ForeignKey("milestones.id"), nullable=True)
    owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="pending")
