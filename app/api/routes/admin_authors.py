from __future__ import annotations

from typing import Generator, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import SessionLocal
from app.models.user import UserRoleEnum
from app.repositories.admin_authors import (
    AuthorAdminError,
    AuthorAdminRepository,
    AuthorListItemData,
    PaginatedAuthors,
)
from app.schemas.admin_author import AuthorCreate, AuthorListItemOut, AuthorListResponse

router = APIRouter(
    prefix="/v1/admin/authors",
    tags=["admin-authors"],
    dependencies=[Depends(require_roles(UserRoleEnum.admin))],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db)) -> AuthorAdminRepository:
    return AuthorAdminRepository(db)


def _serialize_item(item: AuthorListItemData) -> AuthorListItemOut:
    return AuthorListItemOut(
        id=item.id,
        name_ar=item.name_ar,
        name_latin=item.name_latin,
        affiliation=item.affiliation,
        slug=item.slug,
        created_at=item.created_at,
        deleted_at=item.deleted_at,
    )


def _serialize_response(payload: PaginatedAuthors) -> AuthorListResponse:
    return AuthorListResponse(
        items=[_serialize_item(item) for item in payload.items],
        total=payload.total,
        page=payload.page,
        page_size=payload.page_size,
        has_next=payload.has_next,
    )


@router.get("", response_model=AuthorListResponse)
def list_authors(
    q: str | None = Query(default=None, description="Case-insensitive search on latin name."),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    sort: Literal["name", "created_at"] = Query(default="name"),
    status: Literal["active", "deleted", "all"] = Query(default="active"),
    repo: AuthorAdminRepository = Depends(get_repository),
) -> AuthorListResponse:
    payload = repo.list_authors(q=q, page=page, page_size=page_size, sort=sort, status=status)
    return _serialize_response(payload)


@router.post("", response_model=AuthorListItemOut, status_code=status.HTTP_201_CREATED)
def create_author(
    payload: AuthorCreate,
    repo: AuthorAdminRepository = Depends(get_repository),
) -> AuthorListItemOut:
    db = repo.session
    try:
        item = repo.create_author(payload)
        db.commit()
        return _serialize_item(item)
    except AuthorAdminError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail={"user_message": exc.message}) from exc
    except Exception:
        db.rollback()
        raise


@router.patch("/{author_id}/soft-delete", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_author(
    author_id: int = Path(..., ge=1),
    repo: AuthorAdminRepository = Depends(get_repository),
) -> None:
    db = repo.session
    try:
        repo.soft_delete_author(author_id)
        db.commit()
    except AuthorAdminError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail={"user_message": exc.message}) from exc
    except Exception:
        db.rollback()
        raise


@router.patch("/{author_id}/restore", status_code=status.HTTP_204_NO_CONTENT)
def restore_author(
    author_id: int = Path(..., ge=1),
    repo: AuthorAdminRepository = Depends(get_repository),
) -> None:
    db = repo.session
    try:
        repo.restore_author(author_id)
        db.commit()
    except AuthorAdminError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail={"user_message": exc.message}) from exc
    except Exception:
        db.rollback()
        raise


__all__ = ["router", "get_db"]
