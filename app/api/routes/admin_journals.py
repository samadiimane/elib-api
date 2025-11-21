from __future__ import annotations

from typing import Generator, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import SessionLocal
from app.models.user import UserRoleEnum
from app.repositories.admin_journals import (
    JournalAdminError,
    JournalAdminRepository,
    JournalListItemData,
    PaginatedJournals,
)
from app.schemas.admin_journal import (
    JournalCreate,
    JournalListItemOut,
    JournalListResponse,
    JournalUpdate,
)


router = APIRouter(
    prefix="/v1/admin/journals",
    tags=["admin-journals"],
    dependencies=[Depends(require_roles(UserRoleEnum.admin))],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db)) -> JournalAdminRepository:
    return JournalAdminRepository(db)


def _serialize_item(item: JournalListItemData) -> JournalListItemOut:
    return JournalListItemOut(
        id=item.id,
        name=item.name,
        slug=item.slug,
        issn=item.issn,
        description=item.description,
        publisher=item.publisher,
        cover_image_url=item.cover_image_url,
        created_at=item.created_at,
        deleted_at=item.deleted_at,
        issues_count=item.issues_count,
        articles_count=item.articles_count,
    )


def _serialize_response(payload: PaginatedJournals) -> JournalListResponse:
    return JournalListResponse(
        items=[_serialize_item(item) for item in payload.items],
        total=payload.total,
        page=payload.page,
        page_size=payload.page_size,
        has_next=payload.has_next,
    )


def _structured_error(message: str, code: str, status_code: int) -> dict[str, str | int]:
    return {"user_message": message, "code": code, "status": status_code}


def _handle_error(exc: JournalAdminError) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail=_structured_error(exc.user_message, exc.code, exc.status_code),
    )


def _handle_unexpected_error() -> HTTPException:
    return HTTPException(
        status_code=500,
        detail=_structured_error("An unexpected error occurred.", "JOURNALS_UNEXPECTED", 500),
    )


@router.get("", response_model=JournalListResponse)
def list_journals(
    q: str | None = Query(default=None, description="Case-insensitive match on name or slug."),
    status_filter: Literal["active", "deleted", "all"] = Query("active", alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    sort: Literal["name", "created_at"] = Query(default="name"),
    repo: JournalAdminRepository = Depends(get_repository),
) -> JournalListResponse:
    payload = repo.list_journals(
        q=q,
        status=status_filter,
        page=page,
        page_size=page_size,
        sort=sort,
    )
    return _serialize_response(payload)


@router.post("", response_model=JournalListItemOut, status_code=status.HTTP_200_OK)
def create_journal(
    payload: JournalCreate,
    repo: JournalAdminRepository = Depends(get_repository),
) -> JournalListItemOut:
    db = repo.session
    try:
        item = repo.create_journal(payload)
        db.commit()
        return _serialize_item(item)
    except JournalAdminError as exc:
        db.rollback()
        raise _handle_error(exc)
    except Exception:
        db.rollback()
        raise _handle_unexpected_error()


@router.patch("/{journal_id}", response_model=JournalListItemOut)
def update_journal(
    payload: JournalUpdate,
    journal_id: int = Path(..., ge=1),
    repo: JournalAdminRepository = Depends(get_repository),
) -> JournalListItemOut:
    db = repo.session
    try:
        item = repo.update_journal(journal_id, payload)
        db.commit()
        return _serialize_item(item)
    except JournalAdminError as exc:
        db.rollback()
        raise _handle_error(exc)
    except Exception:
        db.rollback()
        raise _handle_unexpected_error()


@router.patch("/{journal_id}/soft-delete", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_journal(
    journal_id: int = Path(..., ge=1),
    repo: JournalAdminRepository = Depends(get_repository),
) -> None:
    db = repo.session
    try:
        repo.soft_delete(journal_id)
        db.commit()
    except JournalAdminError as exc:
        db.rollback()
        raise _handle_error(exc)
    except Exception:
        db.rollback()
        raise _handle_unexpected_error()


@router.patch("/{journal_id}/restore", status_code=status.HTTP_204_NO_CONTENT)
def restore_journal(
    journal_id: int = Path(..., ge=1),
    repo: JournalAdminRepository = Depends(get_repository),
) -> None:
    db = repo.session
    try:
        repo.restore(journal_id)
        db.commit()
    except JournalAdminError as exc:
        db.rollback()
        raise _handle_error(exc)
    except Exception:
        db.rollback()
        raise _handle_unexpected_error()


__all__ = ["router", "get_db"]
