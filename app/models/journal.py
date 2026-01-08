from __future__ import annotations
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.document import Document


class Journal(Base):
    __tablename__ = "journals"
    __table_args__ = (
        Index("ix_journals_name", "name"),
        Index("ix_journals_slug", "slug"),
        Index("ix_journals_created_at", "created_at"),
        Index("ix_journals_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issn: Mapped[str | None] = mapped_column(String(50))
    publisher: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    issues: Mapped[list["JournalIssue"]] = relationship(
        back_populates="journal", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(  # defined in document model
        back_populates="journal"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="journal",
    )
    translations: Mapped[list["JournalTranslation"]] = relationship(
        "JournalTranslation",
        back_populates="journal",
        cascade="all, delete-orphan",
    )


@event.listens_for(Journal, "before_insert")
@event.listens_for(Journal, "before_update")
def _ensure_unique_active_slug(mapper, connection, target: Journal) -> None:
    """SQLite lacks partial unique indexes; block duplicates for active rows."""
    if connection.dialect.name != "sqlite":
        return
    if not target.slug:
        return

    stmt = (
        select(Journal.id)
        .where(Journal.slug == target.slug)
        .where(Journal.deleted_at.is_(None))
    )
    if target.id is not None:
        stmt = stmt.where(Journal.id != target.id)

    exists = connection.execute(stmt.limit(1)).scalar_one_or_none()
    if exists is not None:
        raise ValueError("journal slug must be unique for active entries")

class JournalIssue(Base):
    __tablename__ = "journal_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey("journals.id", ondelete="CASCADE"), nullable=False)
    volume: Mapped[int | None] = mapped_column(Integer)
    number: Mapped[int | None] = mapped_column(Integer)
    year: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255))
    issue_date: Mapped["date | None"] = mapped_column(Date)

    journal: Mapped[Journal] = relationship(back_populates="issues")
    documents: Mapped[list["Document"]] = relationship(  # defined in document model
        back_populates="issue"
    )


class JournalTranslation(Base):
    __tablename__ = "journal_translations"
    __table_args__ = (
        UniqueConstraint("journal_id", "locale", name="uq_journal_translations_journal_locale"),
        Index("ix_journal_translations_journal_id", "journal_id"),
        Index("ix_journal_translations_locale", "locale"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey("journals.id", ondelete="CASCADE"), nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    publisher: Mapped[str | None] = mapped_column(Text, nullable=True)

    journal: Mapped[Journal] = relationship(back_populates="translations")
