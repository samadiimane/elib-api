from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class JournalOut(BaseModel):
    id: int
    name: str
    slug: str
    issn: str | None = None
    description: str | None = None
    publisher: str | None = None
    cover_image_url: str | None = None
    created_at: datetime
    deleted_at: datetime | None = None


class JournalListItemOut(JournalOut):
    issues_count: int
    articles_count: int


class JournalListResponse(BaseModel):
    items: list[JournalListItemOut]
    total: int
    page: int
    page_size: int
    has_next: bool


class JournalCreate(BaseModel):
    name: str
    slug: str | None = None
    issn: str | None = None
    description: str | None = None
    publisher: str | None = None
    cover_image_url: str | None = None


class JournalUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    issn: str | None = None
    description: str | None = None
    publisher: str | None = None
    cover_image_url: str | None = None
