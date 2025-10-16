from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document import Document, DocumentType
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/v1/documents", tags=["documents"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[DocumentOut])
def list_documents(
    q: str | None = Query(default=None, min_length=1),
    type_: DocumentType | None = Query(default=None, alias="type"),
    lang: str | None = Query(default=None, min_length=1, max_length=10),
    year: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[DocumentOut]:
    stmt = select(Document).order_by(Document.created_at.desc())

    if q:
        like_expr = f"%{q}%"
        stmt = stmt.where(Document.title.ilike(like_expr))
    if type_ is not None:
        stmt = stmt.where(Document.type == type_)
    if lang is not None:
        stmt = stmt.where(Document.lang == lang)
    if year is not None:
        stmt = stmt.where(Document.year == year)

    limit = min(page_size, 100)
    offset = (page - 1) * limit

    stmt = stmt.offset(offset).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentOut:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
