from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.db.session import SessionLocal
from app.models.category import Category, CategoryKind
from app.repositories.categories import CategoryRepository
from app.schemas.category import CategoryCounts, CategoryDetailOut, CategoryOut
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
