from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.pagination import PaginatedResponse


class AuthorListItemOut(BaseModel):
    id: int
    name_ar: str
    name_latin: str
    affiliation: str | None = None
    slug: str
    created_at: datetime


class AuthorCreate(BaseModel):
    name_latin: str = Field(min_length=1)
    name_ar: str | None = None
    affiliation: str | None = None


class AuthorListResponse(PaginatedResponse[AuthorListItemOut]):
    """Paginated listing for admin authors."""


__all__ = ["AuthorListItemOut", "AuthorCreate", "AuthorListResponse"]

