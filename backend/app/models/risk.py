from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import RiskSeverity, RiskStatus


class Risk(Base, IDMixin, TimestampMixin):
    __tablename__ = "risks"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_id: Mapped[Optional[str]] = mapped_column(ForeignKey("requirements.id"), nullable=True)
    owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[RiskSeverity] = mapped_column(default=RiskSeverity.MEDIUM)
    likelihood: Mapped[RiskSeverity] = mapped_column(default=RiskSeverity.MEDIUM)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    mitigation: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[RiskStatus] = mapped_column(default=RiskStatus.OPEN)
