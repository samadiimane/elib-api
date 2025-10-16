# app/models/library.py
# Legacy models kept for reference/temporary legacy endpoints. Do NOT export publicly.

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Collection(Base):
    __tablename__ = "collections_legacy"  # was "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    documents: Mapped[list["LegacyDocument"]] = relationship(
        "LegacyDocument",
        back_populates="collection",
        cascade="all,delete-orphan",
    )


class LegacyDocument(Base):
    __tablename__ = "legacy_documents_legacy"  # was "legacy_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    authors: Mapped[str | None] = mapped_column(String(500))  # simple CSV for v1
    lang: Mapped[str | None] = mapped_column(String(10))
    type: Mapped[str | None] = mapped_column(String(50))  # book|journal|thesis|article
    year: Mapped[int | None] = mapped_column(Integer)
    doi: Mapped[str | None] = mapped_column(String(100))
    isbn: Mapped[str | None] = mapped_column(String(50))
    issn: Mapped[str | None] = mapped_column(String(50))
    pages: Mapped[int | None] = mapped_column(Integer)
    abstract: Mapped[str | None] = mapped_column(Text)
    file_key: Mapped[str | None] = mapped_column(String(500))  # storage key (later)

    collection_id: Mapped[int | None] = mapped_column(
        ForeignKey("collections_legacy.id", ondelete="SET NULL")
    )
    collection: Mapped["Collection"] = relationship(back_populates="documents")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
