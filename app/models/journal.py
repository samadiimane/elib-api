from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.document import Document


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issn: Mapped[str | None] = mapped_column(String(50))
    publisher: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

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
