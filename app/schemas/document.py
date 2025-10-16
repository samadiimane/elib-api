from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentType


class PrimaryCategoryRef(BaseModel):
    """Slim representation of a document's primary category."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str


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
    primary_category: PrimaryCategoryRef | None


__all__ = ["DocumentOut", "PrimaryCategoryRef"]
