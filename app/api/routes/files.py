# app/api/routes/files.py
from fastapi import APIRouter, HTTPException, Path
from app.services.storage import object_exists, presigned_get_url

router = APIRouter(prefix="/v1", tags=["files"])

@router.get("/{document_id}/file")
def get_document_file_url(
    document_id: int = Path(..., ge=1),
) -> dict[str, str | int]:
    key = f"/{document_id}.pdf"
    if not object_exists(key):
        raise HTTPException(status_code=404, detail="File not found for this document")
    url = presigned_get_url(key, expires=3600)
    return {"url": url, "expires_in": 3600, "key": key}
