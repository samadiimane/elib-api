# DEPRECATED: legacy route (will be removed)
from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

router = APIRouter(prefix="/v1", tags=["library"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/collections")
def list_collections(db: Session = Depends(get_db)):
    from app.models.library import Collection

    return db.query(Collection).order_by(Collection.name).all()


@router.get("/collections/{collection_id}/documents")
def list_documents_in_collection(
    collection_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.models.library import LegacyDocument

    q = db.query(LegacyDocument).filter(LegacyDocument.collection_id == collection_id)
    return (
        q.order_by(LegacyDocument.year.desc().nulls_last())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@router.get("/documents")
def list_documents(
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.models.library import LegacyDocument

    qry = db.query(LegacyDocument)
    if q:
        like = f"%{q}%"
        qry = qry.filter(LegacyDocument.title.ilike(like))
    return (
        qry.order_by(LegacyDocument.year.desc().nulls_last())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@router.get("/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    from app.models.library import LegacyDocument

    doc = db.get(LegacyDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
