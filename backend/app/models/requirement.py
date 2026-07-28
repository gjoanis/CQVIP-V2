from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import RequirementDisposition, RequirementPriority, RequirementStatus


class Requirement(Base, IDMixin, TimestampMixin):
    __tablename__ = "requirements"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    document_id: Mapped[Optional[str]] = mapped_column(ForeignKey("documents.id"), nullable=True)
    system_id: Mapped[Optional[str]] = mapped_column(ForeignKey("systems.id"), nullable=True)
    req_code: Mapped[str] = mapped_column(String(50), index=True)  # e.g. URS-001
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    priority: Mapped[RequirementPriority] = mapped_column(default=RequirementPriority.MEDIUM)
    status: Mapped[RequirementStatus] = mapped_column(default=RequirementStatus.OPEN)
    source: Mapped[str] = mapped_column(String(255), default="")

    # Validation workflow
    disposition: Mapped[RequirementDisposition] = mapped_column(default=RequirementDisposition.APPLICABLE)
    assigned_to_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assigned_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # AI Assessment (populated by app.ai.requirement_assessment)
    risk: Mapped[str] = mapped_column(String(20), default="")
    gmp_reference: Mapped[str] = mapped_column(String(255), default="")
    acceptance_criteria: Mapped[str] = mapped_column(Text, default="")
    suggested_test: Mapped[str] = mapped_column(Text, default="")
    protocol_section: Mapped[str] = mapped_column(String(50), default="")
    verification_type: Mapped[str] = mapped_column(String(20), default="")

    document: Mapped[Optional["Document"]] = relationship(back_populates="requirements")
