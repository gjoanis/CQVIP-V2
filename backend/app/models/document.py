from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.enums import DocumentStatus


class Document(Base, IDMixin, TimestampMixin):
    __tablename__ = "documents"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    system_id: Mapped[Optional[str]] = mapped_column(ForeignKey("systems.id"), nullable=True)
    uploaded_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(50))  # URS, FS, DS, HDS, SDS, FAT, SAT, IQ, OQ, PQ, ...
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    file_path: Mapped[str] = mapped_column(String(1000))
    checksum: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[DocumentStatus] = mapped_column(default=DocumentStatus.DRAFT)

    requirements: Mapped[list["Requirement"]] = relationship(back_populates="document")
