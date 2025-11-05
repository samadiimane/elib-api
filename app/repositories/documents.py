from __future__ import annotations

from typing import Iterable, Sequence, Tuple

from sqlalchemy import Select, false, func, or_, select
from sqlalchemy.orm import Session, aliased, load_only, selectinload
from sqlalchemy.sql import ColumnElement

from app.models.category import Category
from app.models.author import Author, DocumentAuthor
from app.models.document import Document, DocumentType
from app.repositories.categories import CategoryRepository
from app.services.search import ilike_pattern

DocumentSelect = Select[Tuple[Document]]


def _normalize_sequence(value: Iterable | None) -> tuple:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(value)
    return (value,)


def _apply_author_filter(
    session: Session,
    stmt: DocumentSelect,
    author_query: str | None,
) -> DocumentSelect:
    if not author_query:
        return stmt

    term = author_query.strip()
    if not term:
        return stmt

    bind = session.get_bind()
    dialect_name = bind.dialect.name if bind is not None else None
    pattern = ilike_pattern(term)

    author_alias = aliased(Author, name="author_filter")
    link_alias = aliased(DocumentAuthor, name="document_author_filter")

    def _ilike(column):
        base = func.coalesce(column, "")
        if dialect_name == "postgresql":
            return func.unaccent(base).ilike(func.unaccent(pattern), escape="\\")
        return base.ilike(pattern, escape="\\")

    match_clause = or_(
        _ilike(author_alias.full_name_ar),
        _ilike(author_alias.full_name_lat),
        _ilike(author_alias.affiliation),
    )

    author_subquery = (
        select(link_alias.document_id)
        .join(author_alias, author_alias.id == link_alias.author_id)
        .where(match_clause)
        .distinct()
    )

    return stmt.where(Document.id.in_(author_subquery))


def build_base_filters(
    session: Session,
    *,
    q: str | None = None,
    type_: DocumentType | Sequence[DocumentType] | None = None,
    lang: str | Sequence[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    category_slug: str | None = None,
    include_descendants: bool = False,
    author: str | None = None,
) -> DocumentSelect:
    stmt: DocumentSelect = (
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
                Document.cover_image_url,
                Document.primary_category_id,
            ),
            selectinload(Document.primary_category).load_only(
                Category.id,
                Category.slug,
                Category.name,
            ),
            selectinload(Document.authors).load_only(
                Author.id,
                Author.full_name_ar,
                Author.full_name_lat,
                Author.affiliation,
            ),
        )
        .order_by(None)
    )

    filters: list = []

    if q:
        pattern = ilike_pattern(q)
        filters.append(or_(Document.title.ilike(pattern), Document.abstract.ilike(pattern)))

    type_values = _normalize_sequence(type_)
    if type_values:
        filters.append(Document.type.in_(type_values))

    lang_values = _normalize_sequence(lang)
    if lang_values:
        filters.append(Document.lang.in_(lang_values))

    if year_from is not None:
        filters.append(Document.year >= year_from)

    if year_to is not None:
        filters.append(Document.year <= year_to)

    if category_slug:
        category_row = session.execute(
            select(Category.id, Category.journal_id).where(Category.slug == category_slug)
        ).one_or_none()

        if category_row is None:
            filters.append(false())
        elif category_row.journal_id is not None:
            filters.append(Document.journal_id == category_row.journal_id)
        else:
            category_ids = {category_row.id}
            if include_descendants:
                category_repo = CategoryRepository(session)
                category_ids.update(category_repo.descendant_ids(category_row.id))
            filters.append(Document.primary_category_id.in_(tuple(category_ids)))

    if filters:
        stmt = stmt.where(*filters)

    return _apply_author_filter(session, stmt, author)


def list_documents(
    session: Session,
    base_query: DocumentSelect,
    *,
    sort_clause: ColumnElement,
    page: int,
    page_size: int,
) -> Tuple[list[Document], int]:
    offset = (page - 1) * page_size

    items_stmt = base_query.order_by(sort_clause).offset(offset).limit(page_size)
    count_stmt = base_query.with_only_columns(func.count(Document.id)).order_by(None)

    items = session.execute(items_stmt).scalars().unique().all()
    total = session.execute(count_stmt).scalar_one()
    return items, total


def _base_subquery(base_query: DocumentSelect):
    return base_query.order_by(None).subquery()


def facet_counts_by_type(
    session: Session,
    base_query: DocumentSelect,
) -> list[Tuple[str, int]]:
    subq = _base_subquery(base_query)
    type_col = subq.c.type
    stmt = (
        select(type_col.label("value"), func.count().label("count"))
        .select_from(subq)
        .where(type_col.isnot(None))
        .group_by(type_col)
        .order_by(func.count().desc(), type_col.asc())
    )
    return [
        (row.value, int(row.count))
        for row in session.execute(stmt)
    ]


def facet_counts_by_lang(
    session: Session,
    base_query: DocumentSelect,
    *,
    limit: int = 6,
) -> list[Tuple[str, int]]:
    subq = _base_subquery(base_query)
    lang_col = subq.c.lang
    stmt = (
        select(lang_col.label("value"), func.count().label("count"))
        .select_from(subq)
        .where(lang_col.isnot(None))
        .group_by(lang_col)
        .order_by(func.count().desc(), lang_col.asc())
        .limit(limit)
    )
    return [
        (row.value, int(row.count))
        for row in session.execute(stmt)
    ]


def facet_counts_by_category(
    session: Session,
    base_query: DocumentSelect,
    *,
    limit: int = 10,
) -> list[Tuple[str, str, int]]:
    subq = _base_subquery(base_query)
    stmt = (
        select(
            Category.slug.label("slug"),
            Category.name.label("name"),
            func.count().label("count"),
        )
        .select_from(subq)
        .join(Category, Category.id == subq.c.primary_category_id)
        .where(Category.journal_id.is_(None))
        .group_by(Category.id, Category.slug, Category.name)
        .order_by(func.count().desc(), Category.name.asc())
        .limit(limit)
    )
    return [
        (row.slug, row.name, int(row.count))
        for row in session.execute(stmt)
    ]


def facet_year_range(
    session: Session,
    base_query: DocumentSelect,
) -> Tuple[int | None, int | None]:
    subq = _base_subquery(base_query)
    year_col = subq.c.year
    stmt = (
        select(func.min(year_col).label("min"), func.max(year_col).label("max"))
        .select_from(subq)
        .where(year_col.isnot(None))
    )
    result = session.execute(stmt).one_or_none()
    if not result:
        return None, None
    return result.min, result.max


def facet_year_buckets_decade(
    session: Session,
    base_query: DocumentSelect,
) -> list[Tuple[int, int, int]]:
    subq = _base_subquery(base_query)
    year_col = subq.c.year
    bucket_start = year_col - (year_col % 10)
    bucket_end = bucket_start + 9
    stmt = (
        select(bucket_start.label("from"), bucket_end.label("to"), func.count().label("count"))
        .select_from(subq)
        .where(year_col.isnot(None))
        .group_by(bucket_start, bucket_end)
        .order_by(bucket_start)
    )
    return [
        (
            int(row._mapping["from"]),
            int(row.to),
            int(row.count),
        )
        for row in session.execute(stmt)
    ]


class DocumentRepository:
    """Data access helpers for documents."""

    def __init__(self, session: Session):
        self._session = session

    def build_base_query(
        self,
        *,
        q: str | None = None,
        type_: DocumentType | Sequence[DocumentType] | None = None,
        lang: str | Sequence[str] | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        category_slug: str | None = None,
        include_descendants: bool = False,
        author: str | None = None,
    ) -> DocumentSelect:
        return build_base_filters(
            self._session,
            q=q,
            type_=type_,
            lang=lang,
            year_from=year_min,
            year_to=year_max,
            category_slug=category_slug,
            include_descendants=include_descendants,
            author=author,
        )

    def list(
        self,
        *,
        q: str | None = None,
        type_: DocumentType | None = None,
        lang: str | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        category_slug: str | None = None,
        include_descendants: bool = False,
        order_by: ColumnElement,
        offset: int,
        limit: int,
        author: str | None = None,
    ) -> Tuple[list[Document], int]:
        page_size = max(limit, 1)
        page = (offset // page_size) + 1 if page_size else 1
        base_query = self.build_base_query(
            q=q,
            type_=type_,
            lang=lang,
            year_min=year_min,
            year_max=year_max,
            category_slug=category_slug,
            include_descendants=include_descendants,
            author=author,
        )
        return list_documents(
            self._session,
            base_query,
            sort_clause=order_by,
            page=page,
            page_size=page_size,
        )

    def get_by_id(self, document_id: int) -> Document | None:
        stmt = (
            select(Document)
            .options(
                selectinload(Document.primary_category).load_only(
                    Category.id,
                    Category.slug,
                    Category.name,
                ),
                selectinload(Document.authors).load_only(
                    Author.id,
                    Author.full_name_ar,
                    Author.full_name_lat,
                    Author.affiliation,
                ),
            )
            .where(Document.id == document_id)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def assign_authors(self, document: Document, author_ids: Sequence[int]) -> None:
        """Assign ordered authors to a document by their identifiers."""

        normalized_ids: list[int] = []
        seen: set[int] = set()
        for raw_id in author_ids:
            if raw_id is None:
                continue
            value = int(raw_id)
            if value in seen:
                continue
            normalized_ids.append(value)
            seen.add(value)

        if not normalized_ids:
            document.author_links.clear()
            return

        authors = self._session.execute(
            select(Author).where(Author.id.in_(normalized_ids))
        ).scalars().all()
        authors_by_id = {author.id: author for author in authors}
        missing = [aid for aid in normalized_ids if aid not in authors_by_id]
        if missing:
            raise ValueError(f"Unknown author ids: {missing}")

        existing_links = {link.author_id: link for link in document.author_links}

        for position, author_id in enumerate(normalized_ids, start=1):
            author = authors_by_id[author_id]
            link = existing_links.pop(author_id, None)
            if link is None:
                link = DocumentAuthor(author_id=author.id, position=position)
                document.author_links.append(link)
            else:
                link.position = position

        for leftover in existing_links.values():
            if leftover in document.author_links:
                document.author_links.remove(leftover)
