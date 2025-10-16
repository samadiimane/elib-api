from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum
from sqlalchemy import ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from app.models.category import Category


class DocumentType(str, enum.Enum):
    """Enumerated document artifact types."""

    book = "book"
    article = "article"
    thesis = "thesis"
    report = "report"
    manuscript = "manuscript"
    archive_item = "archive_item"
    site_record = "site_record"
    other = "other"


class Document(Base):
    """Canonical document entry available to end users."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_type", "type"),
        Index("ix_documents_year", "year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)

    type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="doc_type"),
        nullable=False,
    )
    lang: Mapped[str] = mapped_column(String(10), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)

    doi: Mapped[str | None] = mapped_column(String(100), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issn: Mapped[str | None] = mapped_column(String(50), nullable=True)

    primary_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    primary_category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="documents",
    )


__all__ = ["Document", "DocumentType"]
