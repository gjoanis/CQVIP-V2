from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin


class Traceability(Base, IDMixin, TimestampMixin):
    """Links a requirement to the protocol/test step(s) that verify it."""

    __tablename__ = "traceability_links"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    requirement_id: Mapped[str] = mapped_column(ForeignKey("requirements.id"), index=True)
    protocol_id: Mapped[Optional[str]] = mapped_column(ForeignKey("protocols.id"), nullable=True)
    test_step_id: Mapped[Optional[str]] = mapped_column(ForeignKey("test_steps.id"), nullable=True)
    coverage_status: Mapped[str] = mapped_column(String(50), default="uncovered")
