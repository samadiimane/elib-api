from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.document import Document


class Author(Base):
    __tablename__ = "authors"
    __table_args__ = (UniqueConstraint("slug", name="uq_authors_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name_lat: Mapped[str | None] = mapped_column(String(255), nullable=True)
    affiliation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    slug: Mapped[str | None] = mapped_column(String(255), nullable=True)

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

    document_links: Mapped[list["DocumentAuthor"]] = relationship(
        "DocumentAuthor",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DocumentAuthor.position",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary="document_authors",
        back_populates="authors",
        order_by="DocumentAuthor.position",
        viewonly=True,
    )


class DocumentAuthor(Base):
    __tablename__ = "document_authors"
    __table_args__ = (
        Index("ix_document_authors_document_position", "document_id", "position"),
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="author_links",
    )
    author: Mapped[Author] = relationship(
        "Author",
        back_populates="document_links",
    )


__all__ = ["Author", "DocumentAuthor"]
