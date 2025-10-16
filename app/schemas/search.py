from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.document import DocumentOut
from app.schemas.pagination import PaginatedResponse


class FacetCount(BaseModel):
    value: str
    count: int


class FacetCategory(BaseModel):
    slug: str
    name: str
    count: int


class FacetYearBucket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: int = Field(alias="from")
    to: int
    count: int


class FacetYear(BaseModel):
    min: int | None
    max: int | None
    buckets: List[FacetYearBucket]


class SearchFacets(BaseModel):
    type: List[FacetCount]
    lang: List[FacetCount]
    category: List[FacetCategory]
    year: FacetYear


class SearchDocumentsResponse(PaginatedResponse[DocumentOut]):
    facets: SearchFacets


__all__ = [
    "FacetCount",
    "FacetCategory",
    "FacetYearBucket",
    "FacetYear",
    "SearchFacets",
    "SearchDocumentsResponse",
]
