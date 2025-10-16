from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentType


class DocumentOut(BaseModel):
    """Serialized document representation for read APIs."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    abstract: str | None
    type: DocumentType
    lang: str
    year: int | None
    pages: int | None
    doi: str | None
    isbn: str | None
    issn: str | None
    primary_category_id: int | None
    created_at: datetime


__all__ = ["DocumentOut"]
