from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import ValidationStatus


class TestStep(Base, IDMixin, TimestampMixin):
    __tablename__ = "test_steps"

    protocol_id: Mapped[str] = mapped_column(ForeignKey("protocols.id"), index=True)
    step_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, default="")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    actual_result: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ValidationStatus] = mapped_column(default=ValidationStatus.NOT_STARTED)

    protocol: Mapped["Protocol"] = relationship(back_populates="test_steps")
