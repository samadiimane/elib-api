from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.api.dependencies.auth import get_current_user
from app.core.config import settings
from app.models.user import User, UserRoleEnum


router = APIRouter(prefix="/v1/ai", tags=["ai"])

_bearer_scheme = HTTPBearer(auto_error=False)
_ADMIN_ROLES = {"admin", "superadmin"}
_MEMBER_ROLES = {"member", "user", "researcher", "committee"}


class AIChatRequest(BaseModel):
    question: str = Field(min_length=1)
    lang: str = "AR"
    access: str | None = None


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User | None:
    if credentials is None:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise


@router.post("/chat")
def chat(
    payload: AIChatRequest,
    current_user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    rag_payload = {
        "question": payload.question,
        "lang": payload.lang,
        "access": _access_for_user(current_user),
    }
    return _post_rag_chat(rag_payload)


def _access_for_user(user: User | None) -> str:
    if user is None:
        return "public"

    roles = {_role_value(role.role) for role in getattr(user, "roles", [])}
    if roles & _ADMIN_ROLES:
        return "admin"
    if roles & _MEMBER_ROLES:
        return "member"
    return "public"


def _role_value(role: UserRoleEnum | str) -> str:
    if isinstance(role, UserRoleEnum):
        return role.value
    return str(role)


def _post_rag_chat(payload: dict[str, str]) -> dict[str, Any]:
    rag_api_url = settings.rag_api_url.rstrip("/")
    request = Request(
        f"{rag_api_url}/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            if response.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"rag-api error: {body}",
                )
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"rag-api error: {error_body}",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"rag-api connection failed: {exc.reason}",
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"rag-api connection failed: {exc}",
        ) from exc

    try:
        result = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"rag-api invalid JSON: {exc.msg}",
        ) from exc
    if not isinstance(result, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="rag-api invalid JSON: expected object",
        )
    return result


__all__ = ["router"]
