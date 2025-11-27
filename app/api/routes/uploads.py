from __future__ import annotations

from uuid import uuid4
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies.auth import require_roles
from app.core.config import settings
from app.models.user import UserRoleEnum
from app.services.storage import _s3


router = APIRouter(
    prefix="/v1/uploads",
    tags=["uploads"],
    dependencies=[Depends(require_roles(UserRoleEnum.admin, UserRoleEnum.committee))],
)


class PresignUploadOut(BaseModel):
    upload_url: str
    public_url: Optional[str] = None
    key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


@router.post("/presign", response_model=PresignUploadOut)
def presign_upload(payload: dict[str, str]) -> PresignUploadOut:
    content_type = (payload.get("content_type") or "").strip()
    if not content_type:
        raise HTTPException(status_code=400, detail="content_type is required")

    key = f"uploads/{uuid4().hex}"

    try:
        upload_url = _s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.storage_bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to generate upload URL") from exc

    if settings.storage_cdn_base:
        public_url = f"{settings.storage_cdn_base.rstrip('/')}/{key}"
    else:
        endpoint = settings.storage_endpoint.rstrip("/")
        public_url = f"{endpoint}/{settings.storage_bucket}/{key}"

    return PresignUploadOut(
        upload_url=upload_url,
        public_url=public_url,
        key=key,
        headers={"Content-Type": content_type},
    )


__all__ = ["router"]
