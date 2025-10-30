from __future__ import annotations

from typing import Generator, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document import Document, DocumentType
from app.repositories.documents import (
    build_base_filters,
    facet_counts_by_category,
    facet_counts_by_lang,
    facet_counts_by_type,
    facet_year_buckets_decade,
    facet_year_range,
    list_documents,
)
from app.schemas.document import DocumentOut
from app.schemas.search import (
    FacetCategory,
    FacetCount,
    FacetYear,
    FacetYearBucket,
    SearchDocumentsResponse,
    SearchFacets,
)
from app.services.search import validate_sort

router = APIRouter(prefix="/v1/search", tags=["search"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SEARCH_SORTS = {
    "created_desc": desc(Document.created_at),
    "created_asc": asc(Document.created_at),
    "year_desc": desc(Document.year),
    "year_asc": asc(Document.year),
    "title_asc": asc(Document.title),
    "title_desc": desc(Document.title),
}


@router.get("/documents", response_model=SearchDocumentsResponse)
def search_documents(
    q: str | None = Query(default=None, min_length=1),
   type_: List[DocumentType] | None = Query(default=None, alias="type"),
   lang: List[str] | None = Query(default=None),
   year_from: int | None = Query(default=None),
   year_to: int | None = Query(default=None),
   category: str | None = Query(default=None),
    include_descendants: bool = Query(default=False),
   sort: str | None = Query(default="created_desc"),
   page: int = Query(default=1, ge=1),
   page_size: int = Query(default=20, ge=1, le=100),
   db: Session = Depends(get_db),
) -> SearchDocumentsResponse:
    if year_from is not None and year_to is not None and year_from > year_to:
        raise HTTPException(status_code=422, detail="year_from cannot be greater than year_to")

    try:
        order_by = validate_sort(sort, allowed=SEARCH_SORTS, default="created_desc")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    type_filter = type_ or None
    lang_filter = lang or None

    base_query = build_base_filters(
        db,
        q=q,
        type_=type_filter,
        lang=lang_filter,
        year_from=year_from,
        year_to=year_to,
        category_slug=category,
        include_descendants=include_descendants,
    )

    documents, total = list_documents(
        db,
        base_query,
        sort_clause=order_by,
        page=page,
        page_size=page_size,
    )

    items = [DocumentOut.model_validate(doc) for doc in documents]
    has_next = (page - 1) * page_size + len(items) < total

    type_facets = [
        FacetCount(value=value, count=count)
        for value, count in facet_counts_by_type(db, base_query)
    ]
    lang_facets = [
        FacetCount(value=value, count=count)
        for value, count in facet_counts_by_lang(db, base_query)
    ]
    category_facets = [
        FacetCategory(slug=slug, name=name, count=count)
        for slug, name, count in facet_counts_by_category(db, base_query)
    ]

    min_year, max_year = facet_year_range(db, base_query)
    year_buckets = [
        FacetYearBucket(from_=bucket_from, to=bucket_to, count=count)
        for bucket_from, bucket_to, count in facet_year_buckets_decade(db, base_query)
    ]
    facets = SearchFacets(
        type=type_facets,
        lang=lang_facets,
        category=category_facets,
        year=FacetYear(min=min_year, max=max_year, buckets=year_buckets),
    )

    return SearchDocumentsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
        facets=facets,
    )
