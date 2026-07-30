from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import FmeaStatus


class FmeaAnalysis(Base, IDMixin, TimestampMixin):
    """A Process FMEA worksheet for one System/Process -- a container for the
    FmeaLineItem rows, each analyzing one process step's failure modes."""

    __tablename__ = "fmea_analyses"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    system_id: Mapped[str] = mapped_column(ForeignKey("systems.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[FmeaStatus] = mapped_column(default=FmeaStatus.DRAFT)


class FmeaLineItem(Base, IDMixin, TimestampMixin):
    """One process step's failure mode analysis row. severity/occurrence/detection
    are 1-10 (AIAG/VDA-style); rpn = severity * occurrence * detection, recomputed
    server-side on every write so it can never drift from the ratings that produced
    it. The resulting_* fields capture the re-assessment after corrective action."""

    __tablename__ = "fmea_line_items"

    fmea_id: Mapped[str] = mapped_column(ForeignKey("fmea_analyses.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    process_step: Mapped[str] = mapped_column(String(500))
    potential_failure_mode: Mapped[str] = mapped_column(Text, default="")
    potential_effect: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[int] = mapped_column(Integer, default=1)
    potential_cause: Mapped[str] = mapped_column(Text, default="")
    occurrence: Mapped[int] = mapped_column(Integer, default=1)
    current_controls: Mapped[str] = mapped_column(Text, default="")
    detection: Mapped[int] = mapped_column(Integer, default=1)
    rpn: Mapped[int] = mapped_column(Integer, default=1)
    recommended_action: Mapped[str] = mapped_column(Text, default="")
    action_owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    action_taken: Mapped[str] = mapped_column(Text, default="")
    resulting_severity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resulting_occurrence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resulting_detection: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resulting_rpn: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
