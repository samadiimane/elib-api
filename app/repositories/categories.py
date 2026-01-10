from __future__ import annotations

from typing import Iterable, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased, load_only, selectinload
from sqlalchemy.sql import ColumnElement

from app.models.category import Category, CategoryKind
from app.models.journal import Journal
from app.models.document import Document
from app.services.search import build_ilike_pattern
import sqlalchemy as sa

_ct = sa.table(
    "category_translations",
    sa.column("id"),
    sa.column("category_id"),
    sa.column("locale"),
    sa.column("title"),
    sa.column("description"),
)


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
                    Category.journal_id,
                    Category.slug,
                    Category.name,
                    Category.kind,
                    Category.parent_id,
                    Category.description,
                ),
                selectinload(Category.journal).load_only(
                    Journal.id,
                    Journal.slug,
                    Journal.name,
                ),
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
                    Category.journal_id,
                    Category.slug,
                    Category.name,
                    Category.kind,
                    Category.parent_id,
                    Category.description,
                ),
                selectinload(Category.journal).load_only(
                    Journal.id,
                    Journal.slug,
                    Journal.name,
                ),
            )
            .where(Category.slug == slug)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def count_documents_for_category(self, category_id: int) -> int:
        stmt = select(func.count(Document.id)).where(Document.primary_category_id == category_id)
        return self._session.execute(stmt).scalar_one()

    def get_children_by_slug(self, slug: str, kind: str | None = None) -> list[Category]:
        """Return ordered immediate children for the category identified by slug."""
        parent_id = self._session.execute(
            select(Category.id).where(Category.slug == slug)
        ).scalar_one_or_none()
        if parent_id is None:
            return []

        stmt = (
            select(Category)
            .options(
                load_only(
                    Category.id,
                    Category.slug,
                    Category.name,
                    Category.kind,
                    Category.description,
                )
            )
            .where(Category.parent_id == parent_id)
            .order_by(Category.name.asc())
        )

        if kind is not None:
            target_kind = kind
            if not isinstance(target_kind, CategoryKind):
                try:
                    target_kind = CategoryKind(kind)
                except ValueError:
                    return []
            stmt = stmt.where(Category.kind == target_kind)

        return self._session.execute(stmt).scalars().all()

    # Locale-aware helpers -------------------------------------------------
    def _translated_columns(self, locale: str | None):
        ct_locale = aliased(_ct)
        ct_en = aliased(_ct)

        translated_title = sa.func.coalesce(
            ct_locale.c.title if locale else None,
            ct_en.c.title,
            Category.name,
        )
        translated_description = sa.func.coalesce(
            ct_locale.c.description if locale else None,
            ct_en.c.description,
            Category.description,
        )
        joins = []
        if locale:
            joins.append((ct_locale, (ct_locale.c.category_id == Category.id) & (ct_locale.c.locale == locale)))
        joins.append((ct_en, (ct_en.c.category_id == Category.id) & (ct_en.c.locale == "en")))
        return translated_title.label("name"), translated_description.label("description"), joins

    def get_with_locale(self, slug: str, locale: str | None = None):
        translated_title, translated_description, joins = self._translated_columns(
            (locale or "").lower() or None
        )
        stmt = select(
            Category.id,
            Category.slug,
            Category.kind,
            Category.parent_id,
            Category.journal_id,
            Category.order_index,
            Category.created_at,
            translated_title,
            translated_description,
        ).where(Category.slug == slug)
        for alias, condition in joins:
            stmt = stmt.outerjoin(alias, condition)
        row = self._session.execute(stmt).mappings().first()
        return row

    def list_with_locale(
        self,
        *,
        locale: str | None = None,
        parent_id: int | None = None,
        kind: str | None = None,
        search: str | None = None,
        order_by: str | None = "name",
        offset: int = 0,
        limit: int = 20,
    ):
        normalized_locale = (locale or "").lower() or None
        translated_title, translated_description, joins = self._translated_columns(normalized_locale)

        stmt = select(
            Category.id,
            Category.slug,
            Category.kind,
            Category.parent_id,
            Category.journal_id,
            Category.order_index,
            Category.created_at,
            translated_title,
            translated_description,
        )
        count_stmt = select(func.count(Category.id))

        for alias, condition in joins:
            stmt = stmt.outerjoin(alias, condition)
            count_stmt = count_stmt.outerjoin(alias, condition)

        filters: list = []
        if parent_id is not None:
            filters.append(Category.parent_id == parent_id)
        if kind is not None:
            try:
                filters.append(Category.kind == CategoryKind(kind))
            except ValueError:
                filters.append(Category.kind == kind)
        if search:
            pattern = build_ilike_pattern(search)
            filters.append(
                or_(
                    translated_title.ilike(pattern),
                    Category.slug.ilike(pattern),
                )
            )

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        order_exprs = []
        if order_by and order_by.lower() == "name_desc":
            order_exprs.append(sa.func.lower(translated_title).desc())
        else:
            order_exprs.append(sa.func.lower(translated_title).asc())
        order_exprs.append(Category.order_index.asc())
        stmt = stmt.order_by(*order_exprs).offset(offset).limit(limit)

        items = self._session.execute(stmt).mappings().all()
        total = self._session.execute(count_stmt).scalar_one()
        return items, total

    def descendant_ids(self, category_id: int) -> set[int]:
        """Return ids for all descendant categories of the given category id."""
        descendants_cte = (
            select(Category.id)
            .where(Category.parent_id == category_id)
            .cte(name="category_descendants", recursive=True)
        )

        descendants_cte = descendants_cte.union_all(
            select(Category.id).where(Category.parent_id == descendants_cte.c.id)
        )

        descendant_ids: Iterable[int] = self._session.execute(
            select(descendants_cte.c.id)
        ).scalars()
        return set(descendant_ids)
