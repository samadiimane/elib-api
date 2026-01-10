from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.categories import CategoryRepository
from app.schemas.category import CategoryLocalizedOut


def get_category_by_slug(db: Session, slug: str, locale: str | None = None) -> CategoryLocalizedOut | None:
    """Fetch a category with locale-aware title/description fallback."""
    repo = CategoryRepository(db)
    row = repo.get_with_locale(slug, locale)
    if not row:
        return None
    return CategoryLocalizedOut.model_validate(row, from_attributes=False)


def list_categories(
    db: Session,
    *,
    parent_id: int | None = None,
    kind: str | None = None,
    locale: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort: str | None = "name",
    q: str | None = None,
):
    """List categories with locale-aware translations and fallback."""
    repo = CategoryRepository(db)
    offset = max(page - 1, 0) * page_size
    items_rows, total = repo.list_with_locale(
        locale=locale,
        parent_id=parent_id,
        kind=kind,
        search=q,
        order_by=(sort or "name").lower(),
        offset=offset,
        limit=page_size,
    )
    items = [CategoryLocalizedOut.model_validate(row, from_attributes=False) for row in items_rows]
    has_next = offset + len(items) < total
    return items, total, has_next
