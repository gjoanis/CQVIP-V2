from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import ProjectStatus


class Project(Base, IDMixin, TimestampMixin):
    __tablename__ = "projects"

    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), index=True)
    owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(2000), default="")
    status: Mapped[ProjectStatus] = mapped_column(default=ProjectStatus.PLANNING)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    target_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="projects")
    phases: Mapped[list["ProjectPhase"]] = relationship(back_populates="project", cascade="all, delete-orphan")
