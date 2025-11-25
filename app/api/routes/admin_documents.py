from __future__ import annotations

from typing import Generator, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import SessionLocal
from app.models.document import Document, DocumentType
from app.models.user import UserRoleEnum
from app.repositories.admin_documents import AdminDocumentRepository, DocumentAdminError
from app.schemas.admin_document import (
    AdminDocumentCreate,
    AdminDocumentDetailOut,
    AdminDocumentListItemOut,
    AdminDocumentUpdate,
)
from app.schemas.pagination import PaginatedResponse
from app.services.search import validate_sort

router = APIRouter(
    prefix="/v1/admin/documents",
    tags=["admin-documents"],
    dependencies=[Depends(require_roles(UserRoleEnum.admin))],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db)) -> AdminDocumentRepository:
    return AdminDocumentRepository(db)


ADMIN_DOCUMENT_SORTS = {
    "created_at desc": desc(Document.created_at),
    "created_at asc": asc(Document.created_at),
    "updated_at desc": desc(Document.updated_at),
    "updated_at asc": asc(Document.updated_at),
    "year desc": desc(Document.year),
    "year asc": asc(Document.year),
    "title asc": asc(Document.title),
    "title desc": desc(Document.title),
}


@router.get("", response_model=PaginatedResponse[AdminDocumentListItemOut])
def list_admin_documents(
    q: str | None = Query(default=None, min_length=1),
    type_: DocumentType | None = Query(default=None, alias="type"),
    lang: str | None = Query(default=None, min_length=1, max_length=10),
    year_min: int | None = Query(default=None),
    year_max: int | None = Query(default=None),
    category_slug: str | None = Query(default=None, min_length=1),
    journal_id: int | None = Query(default=None, ge=1),
    issue_id: int | None = Query(default=None, ge=1),
    status: Literal["active", "deleted", "all"] = Query(default="active"),
    sort: str | None = Query(default="created_at desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    repo: AdminDocumentRepository = Depends(get_repository),
) -> PaginatedResponse[AdminDocumentListItemOut]:
    if year_min is not None and year_max is not None and year_min > year_max:
        raise HTTPException(status_code=422, detail="year_min cannot be greater than year_max")

    try:
        sort_clause = validate_sort(sort, allowed=ADMIN_DOCUMENT_SORTS, default="created_at desc")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    payload = repo.list_documents(
        q=q,
        type_=type_,
        lang=lang,
        year_min=year_min,
        year_max=year_max,
        category_slug=category_slug,
        journal_id=journal_id,
        issue_id=issue_id,
        status=status,
        sort_clause=sort_clause,
        page=page,
        page_size=page_size,
    )

    items = [AdminDocumentListItemOut.model_validate(item) for item in payload.items]
    return PaginatedResponse[AdminDocumentListItemOut](
        items=items,
        total=payload.total,
        page=payload.page,
        page_size=payload.page_size,
        has_next=payload.has_next,
    )


@router.get("/{document_id}", response_model=AdminDocumentDetailOut)
def get_admin_document(
    document_id: int = Path(..., ge=1),
    repo: AdminDocumentRepository = Depends(get_repository),
) -> AdminDocumentDetailOut:
    document = repo.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return AdminDocumentDetailOut.model_validate(document)


@router.post("", response_model=AdminDocumentDetailOut, status_code=201)
def create_admin_document(
    payload: AdminDocumentCreate,
    repo: AdminDocumentRepository = Depends(get_repository),
) -> AdminDocumentDetailOut:
    db = repo.session
    try:
        document = repo.create_document(payload)
        db.commit()
        return AdminDocumentDetailOut.model_validate(document)
    except DocumentAdminError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail={"user_message": exc.user_message}) from exc
    except Exception:
        db.rollback()
        raise


@router.patch("/{document_id}", response_model=AdminDocumentDetailOut)
def update_admin_document(
    document_id: int = Path(..., ge=1),
    payload: AdminDocumentUpdate | None = None,
    repo: AdminDocumentRepository = Depends(get_repository),
) -> AdminDocumentDetailOut:
    if payload is None:
        payload = AdminDocumentUpdate()
    db = repo.session
    try:
        document = repo.update_document(document_id, payload)
        db.commit()
        return AdminDocumentDetailOut.model_validate(document)
    except DocumentAdminError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail={"user_message": exc.user_message}) from exc
    except Exception:
        db.rollback()
        raise


@router.patch("/{document_id}/delete", response_model=AdminDocumentDetailOut)
def soft_delete_admin_document(
    document_id: int = Path(..., ge=1),
    repo: AdminDocumentRepository = Depends(get_repository),
) -> AdminDocumentDetailOut:
    db = repo.session
    try:
        document = repo.soft_delete_document(document_id)
        db.commit()
        return AdminDocumentDetailOut.model_validate(document)
    except DocumentAdminError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail={"user_message": exc.user_message}) from exc
    except Exception:
        db.rollback()
        raise


@router.patch("/{document_id}/restore", response_model=AdminDocumentDetailOut)
def restore_admin_document(
    document_id: int = Path(..., ge=1),
    repo: AdminDocumentRepository = Depends(get_repository),
) -> AdminDocumentDetailOut:
    db = repo.session
    try:
        document = repo.restore_document(document_id)
        db.commit()
        return AdminDocumentDetailOut.model_validate(document)
    except DocumentAdminError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail={"user_message": exc.user_message}) from exc
    except Exception:
        db.rollback()
        raise


__all__ = ["router", "get_db"]
