from __future__ import annotations
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.journal import Journal


class CategoryKind(str, enum.Enum):
    section = "section"
    journal = "journal"
    archive_collection = "archive_collection"
    topic = "topic"


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_kind", "kind"),
        Index("ix_categories_parent_id", "parent_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    journal_id: Mapped[int | None] = mapped_column(
        ForeignKey("journals.id", ondelete="SET NULL"),
        nullable=True,
    )
    # IMPORTANT: no DB enum; use VARCHAR + CHECK
    kind: Mapped[CategoryKind] = mapped_column(
        SAEnum(CategoryKind, name="category_kind", native_enum=False),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side=lambda: Category.id,
        back_populates="children",
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="primary_category",
    )
    journal: Mapped["Journal | None"] = relationship("Journal", back_populates="categories")


__all__ = ["Category", "CategoryKind"]
