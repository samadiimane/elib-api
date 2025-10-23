from __future__ import annotations
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from app.models.category import Category


class DocumentType(str, enum.Enum):
    book = "book"
    article = "article"
    thesis = "thesis"
    report = "report"
    manuscript = "manuscript"
    archive_item = "archive_item"
    site_record = "site_record"
    other = "other"


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_type", "type"),
        Index("ix_documents_year", "year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)

    # IMPORTANT: no DB enum; use VARCHAR + CHECK
    type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="doc_type", native_enum=False),
        nullable=False,
    )
    lang: Mapped[str] = mapped_column(String(10), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)

    doi: Mapped[str | None] = mapped_column(String(100), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issn: Mapped[str | None] = mapped_column(String(50), nullable=True)

    journal_id: Mapped[int | None] = mapped_column(ForeignKey("journals.id", ondelete="SET NULL"))
    issue_id:   Mapped[int | None] = mapped_column(ForeignKey("journal_issues.id", ondelete="SET NULL"))
    start_page: Mapped[int | None] = mapped_column(Integer)
    end_page:   Mapped[int | None] = mapped_column(Integer)

    journal = relationship("Journal", back_populates="documents")
    issue   = relationship("JournalIssue", back_populates="documents")

    primary_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    primary_category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="documents",
    )


__all__ = ["Document", "DocumentType"]
