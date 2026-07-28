from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import CAPAStatus


class CAPA(Base, IDMixin, TimestampMixin):
    __tablename__ = "capas"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    deviation_id: Mapped[Optional[str]] = mapped_column(ForeignKey("deviations.id"), nullable=True)
    owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    corrective_action: Mapped[str] = mapped_column(Text, default="")
    preventive_action: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[CAPAStatus] = mapped_column(default=CAPAStatus.OPEN)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
