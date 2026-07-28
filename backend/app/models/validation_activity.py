from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import ValidationActivityType, ValidationStatus


class ValidationActivity(Base, IDMixin, TimestampMixin):
    __tablename__ = "validation_activities"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    activity_type: Mapped[ValidationActivityType] = mapped_column(default=ValidationActivityType.OTHER)
    status: Mapped[ValidationStatus] = mapped_column(default=ValidationStatus.NOT_STARTED)
    planned_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    protocols: Mapped[list["Protocol"]] = relationship(back_populates="validation_activity")
