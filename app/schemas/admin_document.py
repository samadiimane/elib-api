from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryKind
from app.models.document import DocumentType


class AdminDocumentAuthorRef(BaseModel):
    """Slim author reference for admin document responses."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name_ar: str = Field(validation_alias="full_name_ar")
    name_lat: str | None = Field(default=None, validation_alias="full_name_lat")


class AdminDocumentPrimaryCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    kind: CategoryKind


class AdminDocumentJournalRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str


class AdminDocumentIssueRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int | None = None
    volume: int | None = None
    number: int | None = None
    title: str | None = None


class AdminDocumentListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: DocumentType
    lang: str
    year: int | None = None
    pages: int | None = None
    primary_category: AdminDocumentPrimaryCategory | None = None
    journal: AdminDocumentJournalRef | None = None
    issue: AdminDocumentIssueRef | None = None
    authors: list[AdminDocumentAuthorRef] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    status: str | None = "active"


class AdminDocumentDetailOut(AdminDocumentListItemOut):
    doi: str | None = None
    isbn: str | None = None
    issn: str | None = None
    abstract: str | None = None
    cover_image_url: str | None = None
    start_page: int | None = None
    end_page: int | None = None
    file_key: str | None = None


class AdminDocumentCreate(BaseModel):
    title: str
    abstract: str | None = None
    type: DocumentType | None = None
    lang: str
    year: int | None = None
    pages: int | None = None
    doi: str | None = None
    isbn: str | None = None
    issn: str | None = None
    primary_category_id: int | None = None
    journal_id: int | None = None
    issue_id: int | None = None
    cover_image_url: str | None = None
    start_page: int | None = None
    end_page: int | None = None
    author_ids: list[int] | None = None
    file_key: str | None = None


class AdminDocumentUpdate(BaseModel):
    title: str | None = None
    abstract: str | None = None
    type: DocumentType | None = None
    lang: str | None = None
    year: int | None = None
    pages: int | None = None
    doi: str | None = None
    isbn: str | None = None
    issn: str | None = None
    primary_category_id: int | None = None
    journal_id: int | None = None
    issue_id: int | None = None
    cover_image_url: str | None = None
    start_page: int | None = None
    end_page: int | None = None
    author_ids: list[int] | None = None
    file_key: str | None = None


__all__ = [
    "AdminDocumentAuthorRef",
    "AdminDocumentPrimaryCategory",
    "AdminDocumentJournalRef",
    "AdminDocumentIssueRef",
    "AdminDocumentListItemOut",
    "AdminDocumentDetailOut",
    "AdminDocumentCreate",
    "AdminDocumentUpdate",
]
