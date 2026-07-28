from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin


class RequirementRelationship(Base, IDMixin):
    __tablename__ = "requirement_relationships"

    source_requirement_id: Mapped[str] = mapped_column(ForeignKey("requirements.id"), index=True)
    target_requirement_id: Mapped[str] = mapped_column(ForeignKey("requirements.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(50))  # derives_from, conflicts_with, duplicates, ...
