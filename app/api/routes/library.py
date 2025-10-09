from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.library import Collection, Document

router = APIRouter(prefix="/v1", tags=["library"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/collections")
def list_collections(db: Session = Depends(get_db)):
    return db.query(Collection).order_by(Collection.name).all()

@router.get("/collections/{collection_id}/documents")
def list_documents_in_collection(
    collection_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Document).filter(Document.collection_id == collection_id)
    return q.order_by(Document.year.desc().nulls_last()) \
            .offset((page-1)*page_size).limit(page_size).all()

@router.get("/documents")
def list_documents(
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    qry = db.query(Document)
    if q:
        like = f"%{q}%"
        qry = qry.filter(Document.title.ilike(like))
    return qry.order_by(Document.year.desc().nulls_last()) \
              .offset((page-1)*page_size).limit(page_size).all()

@router.get("/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
