from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document import Document, DocumentType
from app.repositories.documents import (
    DocumentRepository,
    build_base_filters,
    list_documents as list_documents_query,
)
from app.schemas.document import DocumentOut
from app.schemas.pagination import PaginatedResponse
from app.services.search import validate_sort

router = APIRouter(prefix="/v1/documents", tags=["documents"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DOCUMENT_SORTS = {
    "created_at desc": desc(Document.created_at),
    "created_at asc": asc(Document.created_at),
    "created_desc": desc(Document.created_at),
    "created_asc": asc(Document.created_at),
    "year desc": desc(Document.year),
    "year asc": asc(Document.year),
    "year_desc": desc(Document.year),
    "year_asc": asc(Document.year),
    "title asc": asc(Document.title),
    "title desc": desc(Document.title),
    "title_asc": asc(Document.title),
    "title_desc": desc(Document.title),
}


@router.get("", response_model=PaginatedResponse[DocumentOut])
def list_documents(
    q: str | None = Query(default=None, min_length=1),
    type_: DocumentType | None = Query(default=None, alias="type"),
    lang: str | None = Query(default=None, min_length=1, max_length=10),
    year_min: int | None = Query(default=None),
    year_max: int | None = Query(default=None),
    category_slug: str | None = Query(default=None, min_length=1),
    sort: str | None = Query(default="created_at desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[DocumentOut]:
    if year_min is not None and year_max is not None and year_min > year_max:
        raise HTTPException(status_code=422, detail="year_min cannot be greater than year_max")

    try:
        order_by = validate_sort(sort, allowed=DOCUMENT_SORTS, default="created_at desc")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    base_query = build_base_filters(
        db,
        q=q,
        type_=type_,
        lang=lang,
        year_from=year_min,
        year_to=year_max,
        category_slug=category_slug,
    )
    documents, total = list_documents_query(
        db,
        base_query,
        sort_clause=order_by,
        page=page,
        page_size=page_size,
    )

    items = [DocumentOut.model_validate(doc) for doc in documents]
    has_next = (page - 1) * page_size + len(items) < total

    return PaginatedResponse[DocumentOut](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
    )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentOut:
    repository = DocumentRepository(db)
    document = repository.get_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentOut.model_validate(document)
