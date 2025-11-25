# app/api/routes/files.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.document import Document
from app.services.storage import object_exists, presigned_get_url

router = APIRouter(prefix="/v1", tags=["files"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{document_id}/file")
def get_document_file_url(
    document_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> dict[str, str | int]:
    document = db.get(Document, document_id)
    key = document.file_key if document and document.file_key else f"/{document_id}.pdf"
    if not object_exists(key):
        raise HTTPException(status_code=404, detail="File not found for this document")
    url = presigned_get_url(key, expires=3600)
    return {"url": url, "expires_in": 3600, "key": key}
