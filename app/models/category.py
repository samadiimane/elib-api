from __future__ import annotations
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func
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
        UniqueConstraint("kind", "slug", name="uq_categories_kind_slug"),
        Index("ix_categories_kind", "kind"),
        Index("ix_categories_parent_id", "parent_id"),
        Index("ix_categories_parent_order", "parent_id", "order_index"),
        Index("ix_categories_slug", "slug"),
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
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

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
