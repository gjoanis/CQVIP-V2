from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import SystemType


class System(Base, IDMixin, TimestampMixin):
    """A piece of equipment, facility/utility system, computerized system, or
    manufacturing process that URS/SOP/PM/Work Instruction documents and
    requirements trace back to."""

    __tablename__ = "systems"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    system_type: Mapped[SystemType] = mapped_column(default=SystemType.EQUIPMENT)
    identifier: Mapped[str] = mapped_column(String(100), default="")  # asset tag / system ID
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(255), default="")
