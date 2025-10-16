from __future__ import annotations

from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.category import Category, CategoryKind
from app.schemas.category import CategoryOut

router = APIRouter(prefix="/v1/categories", tags=["categories"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[CategoryOut])
def list_categories(
    kind: CategoryKind | None = Query(default=None),
    parent_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
) -> list[CategoryOut]:
    stmt = select(Category).order_by(Category.name)
    if kind is not None:
        stmt = stmt.where(Category.kind == kind)
    if parent_id is not None:
        stmt = stmt.where(Category.parent_id == parent_id)
    result = db.execute(stmt)
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> CategoryOut:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
