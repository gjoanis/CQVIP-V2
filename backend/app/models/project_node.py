from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin


class ProjectNode(Base, IDMixin, TimestampMixin):
    """Generic tree node backing the Project Workspace navigator (folders, sections, links)."""

    __tablename__ = "project_nodes"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    parent_id: Mapped[Optional[str]] = mapped_column(ForeignKey("project_nodes.id"), nullable=True)
    node_type: Mapped[str] = mapped_column(String(50))  # e.g. folder, document_link, phase_link
    name: Mapped[str] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, default=0)
