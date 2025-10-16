from __future__ import annotations

from typing import Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased, load_only
from sqlalchemy.sql import ColumnElement

from app.models.category import Category, CategoryKind
from app.models.document import Document
from app.services.search import build_ilike_pattern


class CategoryRepository:
    """Data access helpers for categories."""

    def __init__(self, session: Session):
        self._session = session

    def list(
        self,
        *,
        kind: CategoryKind | None = None,
        parent_slug: str | None = None,
        search: str | None = None,
        order_by: ColumnElement,
        offset: int,
        limit: int,
    ) -> Tuple[list[Category], int]:
        stmt = (
            select(Category)
            .options(
                load_only(
                    Category.id,
                    Category.slug,
                    Category.name,
                    Category.kind,
                    Category.parent_id,
                    Category.description,
                )
            )
        )
        count_stmt = select(func.count(Category.id))

        parent_alias = None
        if parent_slug:
            parent_alias = aliased(Category)
            stmt = stmt.join(parent_alias, Category.parent)
            count_stmt = count_stmt.join(parent_alias, Category.parent)

        filters: list = []

        if parent_slug and parent_alias is not None:
            filters.append(parent_alias.slug == parent_slug)

        if kind is not None:
            filters.append(Category.kind == kind)

        if search:
            pattern = build_ilike_pattern(search)
            filters.append(or_(Category.name.ilike(pattern), Category.slug.ilike(pattern)))

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        stmt = stmt.order_by(order_by).offset(offset).limit(limit)

        items = self._session.execute(stmt).scalars().unique().all()
        total = self._session.execute(count_stmt).scalar_one()
        return items, total

    def get_by_slug(self, slug: str) -> Category | None:
        stmt = (
            select(Category)
            .options(
                load_only(
                    Category.id,
                    Category.slug,
                    Category.name,
                    Category.kind,
                    Category.parent_id,
                    Category.description,
                )
            )
            .where(Category.slug == slug)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def count_documents_for_category(self, category_id: int) -> int:
        stmt = select(func.count(Document.id)).where(Document.primary_category_id == category_id)
        return self._session.execute(stmt).scalar_one()
