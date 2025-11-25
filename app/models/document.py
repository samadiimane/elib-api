from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    event,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.journal import Journal, JournalIssue
    from app.models.author import Author, DocumentAuthor


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
        Index("ix_documents_deleted_at", "deleted_at"),
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
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    journal_id: Mapped[int | None] = mapped_column(ForeignKey("journals.id", ondelete="SET NULL"))
    issue_id:   Mapped[int | None] = mapped_column(ForeignKey("journal_issues.id", ondelete="SET NULL"))
    start_page: Mapped[int | None] = mapped_column(Integer)
    end_page:   Mapped[int | None] = mapped_column(Integer)

    journal = relationship("Journal", back_populates="documents")
    issue = relationship("JournalIssue", back_populates="documents")

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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    primary_category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="documents",
    )
    author_links: Mapped[list["DocumentAuthor"]] = relationship(
        "DocumentAuthor",
        back_populates="document",
        order_by="DocumentAuthor.position",
        cascade="all, delete-orphan",
    )
    authors: Mapped[list["Author"]] = relationship(
        "Author",
        secondary="document_authors",
        back_populates="documents",
        order_by="DocumentAuthor.position",
        viewonly=True,
    )

    @property
    def status(self) -> str:
        return "deleted" if self.deleted_at is not None else "active"


__all__ = ["Document", "DocumentType"]


@event.listens_for(Document, "before_insert")
@event.listens_for(Document, "before_update")
def _sync_journal_with_issue(mapper, connection, target: Document) -> None:
    """Ensure documents with an issue automatically align their journal."""
    if target.issue_id is None:
        return

    from app.models.journal import JournalIssue  # Local import to avoid circular deps

    issue_journal_id = connection.execute(
        select(JournalIssue.journal_id).where(JournalIssue.id == target.issue_id)
    ).scalar_one_or_none()

    if issue_journal_id is None:
        raise ValueError(f"Document issue_id {target.issue_id} does not reference a valid journal")

    if target.journal_id is None:
        target.journal_id = issue_journal_id
        return

    if target.journal_id != issue_journal_id:
        raise ValueError(
            "Document journal_id must match the journal for the associated issue "
            f"(issue {target.issue_id} → journal {issue_journal_id}, got {target.journal_id})"
        )
