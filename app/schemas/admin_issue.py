from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class AdminIssueListItemOut(BaseModel):
    id: int
    journal_id: int
    volume: int | None = None
    number: int | None = None
    year: int | None = None
    title: str | None = None
    cover_image_url: str | None = None
    published_at: datetime | None = None
    articles_count: int
    created_at: datetime | None = None


class AdminIssueListResponse(BaseModel):
    items: list[AdminIssueListItemOut]
    total: int
    page: int
    page_size: int
    has_next: bool


class AdminIssueCreate(BaseModel):
    title: str | None = None
    year: int | None = None
    number: int | None = None
    volume: int | None = None
    published_at: datetime | None = None


class AdminIssueUpdate(BaseModel):
    title: str | None = None
    year: int | None = None
    number: int | None = None
    volume: int | None = None
    published_at: datetime | None = None


__all__ = [
    "AdminIssueListItemOut",
    "AdminIssueListResponse",
    "AdminIssueCreate",
    "AdminIssueUpdate",
]
