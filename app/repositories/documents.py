from __future__ import annotations

from typing import Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased, load_only, selectinload
from sqlalchemy.sql import ColumnElement

from app.models.category import Category
from app.models.document import Document, DocumentType
from app.services.search import build_ilike_pattern


class DocumentRepository:
    """Data access helpers for documents."""

    def __init__(self, session: Session):
        self._session = session

    def list(
        self,
        *,
        q: str | None = None,
        type_: DocumentType | None = None,
        lang: str | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        category_slug: str | None = None,
        order_by: ColumnElement,
        offset: int,
        limit: int,
    ) -> Tuple[list[Document], int]:
        stmt = (
            select(Document)
            .options(
                load_only(
                    Document.id,
                    Document.title,
                    Document.abstract,
                    Document.type,
                    Document.lang,
                    Document.year,
                    Document.pages,
                    Document.doi,
                    Document.isbn,
                    Document.issn,
                    Document.primary_category_id,
                ),
                selectinload(Document.primary_category).load_only(
                    Category.id,
                    Category.slug,
                    Category.name,
                ),
            )
        )
        count_stmt = select(func.count(Document.id))

        filters: list = []

        if q:
            pattern = build_ilike_pattern(q)
            filters.append(or_(Document.title.ilike(pattern), Document.abstract.ilike(pattern)))

        if type_ is not None:
            filters.append(Document.type == type_)

        if lang:
            filters.append(Document.lang == lang)

        if year_min is not None:
            filters.append(Document.year >= year_min)

        if year_max is not None:
            filters.append(Document.year <= year_max)

        if category_slug:
            category_alias = aliased(Category)
            stmt = stmt.join(category_alias, Document.primary_category)
            count_stmt = count_stmt.join(category_alias, Document.primary_category)
            filters.append(category_alias.slug == category_slug)

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        stmt = stmt.order_by(order_by).offset(offset).limit(limit)

        items = self._session.execute(stmt).scalars().unique().all()
        total = self._session.execute(count_stmt).scalar_one()
        return items, total

    def get_by_id(self, document_id: int) -> Document | None:
        stmt = (
            select(Document)
            .options(
                selectinload(Document.primary_category).load_only(
                    Category.id,
                    Category.slug,
                    Category.name,
                )
            )
            .where(Document.id == document_id)
        )
        return self._session.execute(stmt).scalar_one_or_none()
