from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import SessionLocal
from app.models.category import CategoryKind
from app.models.user import UserRoleEnum
from app.repositories.admin_categories import (
    CategoryAdminError,
    CategoryAdminRepository,
    CategoryListItemData,
    CategoryNodeData,
)
from app.schemas.admin_category import (
    CategoryCreate,
    CategoryListItemOut,
    CategoryListResponse,
    CategoryMoveRequest,
    CategoryNodeOut,
    CategoryPathFragment,
    CategoryReorderRequest,
    CategoryUpdate,
    ReorderItem,
)

router = APIRouter(
    prefix="/v1/admin/categories",
    tags=["admin-categories"],
    dependencies=[Depends(require_roles(UserRoleEnum.admin))],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db)) -> CategoryAdminRepository:
    return CategoryAdminRepository(db)


def _serialize_node(node: CategoryNodeData) -> CategoryNodeOut:
    children = [_serialize_node(child) for child in node.children] if node.children else None
    return CategoryNodeOut(
        id=node.id,
        name=node.name,
        slug=node.slug,
        kind=node.kind,
        parent_id=node.parent_id,
        order=node.order,
        document_count=node.document_count,
        children=children,
    )


def _serialize_list_item(item: CategoryListItemData) -> CategoryListItemOut:
    return CategoryListItemOut(
        id=item.id,
        name=item.name,
        slug=item.slug,
        kind=item.kind,
        parent_id=item.parent_id,
        order=item.order,
        document_count=item.document_count,
        created_at=item.created_at,
        path=[CategoryPathFragment(id=frag.id, slug=frag.slug, name=frag.name) for frag in item.path],
    )


def _serialize_category(category, repo: CategoryAdminRepository) -> CategoryNodeOut:
    return CategoryNodeOut(
        id=category.id,
        name=category.name,
        slug=category.slug,
        kind=category.kind,
        parent_id=category.parent_id,
        order=category.order_index,
        document_count=repo.document_count(category.id),
        children=None,
    )


def _handle_admin_error(error: CategoryAdminError) -> None:
    raise HTTPException(
        status_code=error.status_code,
        detail={"user_message": error.message},
    )


@router.get("/tree", response_model=list[CategoryNodeOut])
def get_category_tree(
    kind: CategoryKind | None = Query(default=None),
    max_depth: int = Query(default=2, ge=1, le=6),
    include_counts: bool = Query(default=True),
    repo: CategoryAdminRepository = Depends(get_repository),
) -> list[CategoryNodeOut]:
    nodes = repo.get_tree(kind=kind, max_depth=max_depth, include_counts=include_counts)
    return [_serialize_node(node) for node in nodes]


@router.get("/children/{parent_id}", response_model=list[CategoryNodeOut])
def get_category_children(
    parent_id: int = Path(..., ge=1),
    repo: CategoryAdminRepository = Depends(get_repository),
) -> list[CategoryNodeOut]:
    nodes = repo.get_children(parent_id=parent_id, include_counts=True)
    return [_serialize_node(node) for node in nodes]


@router.get("/list", response_model=CategoryListResponse)
def list_categories(
    q: str = Query(default=""),
    kind: CategoryKind | None = Query(default=None),
    parent_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    sort: str = Query(default="name", pattern="^(name|created_at)$"),
    repo: CategoryAdminRepository = Depends(get_repository),
) -> CategoryListResponse:
    items, total = repo.list_categories(
        search=q.strip() or None,
        kind=kind,
        parent_id=parent_id,
        page=page,
        page_size=page_size,
        sort=sort if sort in {"name", "created_at"} else "name",
    )
    return CategoryListResponse(
        items=[_serialize_list_item(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=page * page_size < total,
    )


@router.post("", response_model=CategoryNodeOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    repo: CategoryAdminRepository = Depends(get_repository),
) -> CategoryNodeOut:
    db = repo.session
    try:
        category = repo.create_category(
            name=payload.name,
            slug=payload.slug,
            kind=payload.kind,
            parent_id=payload.parent_id,
            order=payload.order,
        )
        db.commit()
        db.refresh(category)
        return _serialize_category(category, repo)
    except CategoryAdminError as exc:
        db.rollback()
        _handle_admin_error(exc)
    except Exception:
        db.rollback()
        raise


@router.patch("/reorder")
def reorder_categories(
    payload: CategoryReorderRequest,
    repo: CategoryAdminRepository = Depends(get_repository),
) -> dict[str, str]:
    db = repo.session
    try:
        repo.reorder_siblings(
            parent_id=payload.parent_id,
            items=[(item.id, item.order) for item in payload.items],
        )
        db.commit()
        return {"status": "ok"}
    except CategoryAdminError as exc:
        db.rollback()
        _handle_admin_error(exc)
    except Exception:
        db.rollback()
        raise


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int = Path(..., ge=1),
    repo: CategoryAdminRepository = Depends(get_repository),
) -> None:
    db = repo.session
    try:
        repo.delete_category(category_id)
        db.commit()
    except CategoryAdminError as exc:
        db.rollback()
        _handle_admin_error(exc)
    except Exception:
        db.rollback()
        raise
@router.patch("/{category_id}", response_model=CategoryNodeOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    repo: CategoryAdminRepository = Depends(get_repository),
) -> CategoryNodeOut:
    db = repo.session
    try:
        category = repo.update_category(
            category_id,
            name=payload.name,
            slug=payload.slug,
        )
        db.commit()
        db.refresh(category)
        return _serialize_category(category, repo)
    except CategoryAdminError as exc:
        db.rollback()
        _handle_admin_error(exc)
    except Exception:
        db.rollback()
        raise


@router.patch("/{category_id}/move", response_model=CategoryNodeOut)
def move_category(
    category_id: int,
    payload: CategoryMoveRequest,
    repo: CategoryAdminRepository = Depends(get_repository),
) -> CategoryNodeOut:
    db = repo.session
    try:
        category = repo.move_category(
            category_id,
            parent_id=payload.parent_id,
            order=payload.order,
        )
        db.commit()
        db.refresh(category)
        return _serialize_category(category, repo)
    except CategoryAdminError as exc:
        db.rollback()
        _handle_admin_error(exc)
    except Exception:
        db.rollback()
        raise

