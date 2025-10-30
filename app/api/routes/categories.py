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
)
from app.schemas.pagination import PaginatedResponse
from app.services.search import validate_sort

router = APIRouter(prefix="/v1/categories", tags=["categories"])


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

@router.get("/{slug}/children", response_model=CategoryChildrenResponse)
def list_category_children(
    slug: str,
    kind: CategoryKind | None = Query(default=None),
    with_counts: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> CategoryChildrenResponse:
    repository = CategoryRepository(db)
    parent = repository.get_by_slug(slug)
    if parent is None:
        raise HTTPException(status_code=404, detail="Category not found")

    kind_filter = kind.value if isinstance(kind, CategoryKind) else None
    children = repository.get_children_by_slug(slug, kind=kind_filter)
    counts_by_child: dict[int, CategoryCounts] = {}

    if with_counts and children:
        counts_by_child = {}
        for child in children:
            count_stmt = (
                build_base_filters(
                    db,
                    category_slug=child.slug,
                    include_descendants=True,
                )
                .with_only_columns(func.count())
                .order_by(None)
            )
            count_value = db.execute(count_stmt).scalar_one()
            counts_by_child[child.id] = CategoryCounts(documents=count_value)

    items: list[CategoryChildOut] = []
    for child in children:
        base = CategoryChildOut.model_validate(child)
        if with_counts:
            base = base.model_copy(update={"counts": counts_by_child.get(child.id)})
        items.append(base)

    return CategoryChildrenResponse(items=items)


@router.get("", response_model=PaginatedResponse[CategoryOut])
def list_categories(
    kind: CategoryKind | None = Query(default=None),
    parent_slug: str | None = Query(default=None, min_length=1),
    search: str | None = Query(default=None, min_length=1),
    sort: str | None = Query(default="name asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[CategoryOut]:
    repository = CategoryRepository(db)
    try:
        order_by = validate_sort(sort, allowed=CATEGORY_SORTS, default="name asc")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    offset = (page - 1) * page_size
    categories, total = repository.list(
        kind=kind,
        parent_slug=parent_slug,
        search=search,
        order_by=order_by,
        offset=offset,
        limit=page_size,
    )

    items = [CategoryOut.model_validate(cat) for cat in categories]
    has_next = offset + len(items) < total

    return PaginatedResponse[CategoryOut](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
    )


@router.get("/{slug}", response_model=CategoryDetailOut)
def get_category(
    slug: str,
    db: Session = Depends(get_db),
) -> CategoryDetailOut:
    repository = CategoryRepository(db)
    category = repository.get_by_slug(slug)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    counts = CategoryCounts(documents=repository.count_documents_for_category(category.id))
    return CategoryDetailOut(
        category=CategoryOut.model_validate(category),
        counts=counts,
    )
