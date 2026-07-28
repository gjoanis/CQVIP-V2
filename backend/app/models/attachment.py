from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin


class Attachment(Base, IDMixin, TimestampMixin):
    """Polymorphic attachment: entity_type + entity_id point at any other table's row."""

    __tablename__ = "attachments"

    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    uploaded_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[str] = mapped_column(String(1000))
    content_type: Mapped[str] = mapped_column(String(100), default="")
    document_type: Mapped[str] = mapped_column(String(100), default="")
