from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, func

from app.db.session import SessionLocal
from app.models.category import Category, CategoryKind
from app.repositories.categories import CategoryRepository
from app.repositories.documents import build_base_filters
from app.schemas.category import (
    CategoryChildOut,
    CategoryChildrenResponse,
    CategoryCounts,
    CategoryDetailOut,
    CategoryOut,
    CategoryLocalizedOut,
)
from app.schemas.pagination import PaginatedResponse
from app.services.search import validate_sort
from app.services import categories_localized

router = APIRouter(prefix="/v1/categories", tags=["categories"])

ALLOWED_LOCALES = {"en", "fr", "es", "ar"}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


CATEGORY_SORTS = {
    "name asc": asc(Category.name),
    "name desc": desc(Category.name),
}


def _validate_locale(locale: str | None) -> str | None:
    if locale is None:
        return None
    loc = (locale or "").lower()
    if loc not in ALLOWED_LOCALES:
        raise HTTPException(status_code=422, detail="Invalid locale")
    return loc

@router.get("/{slug}/children", response_model=CategoryChildrenResponse)
def list_category_children(
    slug: str,
    kind: CategoryKind | None = Query(default=None),
    with_counts: bool = Query(default=False),
    locale: str | None = Query(default=None, min_length=2, max_length=5),
    db: Session = Depends(get_db),
) -> CategoryChildrenResponse:
    loc = _validate_locale(locale)
    repository = CategoryRepository(db)
    parent = repository.get_with_locale(slug, loc)
    if parent is None:
        raise HTTPException(status_code=404, detail="Category not found")

    parent_id = parent["id"]
    kind_filter = kind.value if isinstance(kind, CategoryKind) else None
    children_rows, _ = repository.list_with_locale(
        locale=loc,
        parent_id=parent_id,
        kind=kind_filter,
        search=None,
        order_by="name",
        offset=0,
        limit=500,
    )
    counts_by_child: dict[int, CategoryCounts] = {}

    if with_counts and children_rows:
        for child in children_rows:
            count_stmt = (
                build_base_filters(
                    db,
                    category_slug=child["slug"],
                    include_descendants=True,
                )
                .with_only_columns(func.count())
                .order_by(None)
            )
            count_value = db.execute(count_stmt).scalar_one()
            counts_by_child[child["id"]] = CategoryCounts(documents=count_value)

    items: list[CategoryChildOut] = []
    for child in children_rows:
        base = CategoryChildOut.model_validate(child, from_attributes=False)
        if with_counts:
            base = base.model_copy(update={"counts": counts_by_child.get(child["id"])})
        items.append(base)

    return CategoryChildrenResponse(items=items)


@router.get("", response_model=PaginatedResponse[CategoryLocalizedOut])
def list_categories(
    kind: CategoryKind | None = Query(default=None),
    parent_slug: str | None = Query(default=None, min_length=1),
    search: str | None = Query(default=None, min_length=1),
    sort: str | None = Query(default="name asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    locale: str | None = Query(default=None, min_length=2, max_length=5),
    db: Session = Depends(get_db),
) -> PaginatedResponse[CategoryLocalizedOut]:
    loc = _validate_locale(locale)
    try:
        order_by = validate_sort(sort, allowed=CATEGORY_SORTS, default="name asc")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    sort_key = "name_desc" if order_by == CATEGORY_SORTS["name desc"] else "name"

    # Resolve parent id if provided
    parent_id = None
    if parent_slug:
        parent_row = CategoryRepository(db).get_with_locale(parent_slug, loc)
        if parent_row:
            parent_id = parent_row["id"]
        else:
            return PaginatedResponse[CategoryLocalizedOut](
                items=[], total=0, page=page, page_size=page_size, has_next=False
            )

    items, total, has_next = categories_localized.list_categories(
        db,
        parent_id=parent_id,
        kind=kind.value if isinstance(kind, CategoryKind) else kind,
        locale=loc,
        page=page,
        page_size=page_size,
        sort=sort_key,
        q=search,
    )

    return PaginatedResponse[CategoryLocalizedOut](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
    )


@router.get("/{slug}", response_model=CategoryDetailOut)
def get_category(
    slug: str,
    locale: str | None = Query(default=None, min_length=2, max_length=5),
    db: Session = Depends(get_db),
) -> CategoryDetailOut:
    loc = _validate_locale(locale)
    repository = CategoryRepository(db)
    category = categories_localized.get_category_by_slug(db, slug, loc)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    counts = CategoryCounts(documents=repository.count_documents_for_category(category.id))
    return CategoryDetailOut(
        category=CategoryOut.model_validate(category, from_attributes=True),
        counts=counts,
    )
