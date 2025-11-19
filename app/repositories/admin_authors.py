from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.author import Author
from app.schemas.admin_author import AuthorCreate


class AuthorAdminError(Exception):
    """Domain error for admin author operations."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


SlugPattern = re.compile(r"[^a-z0-9]+")


def slugify_value(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = SlugPattern.sub("-", ascii_value.lower()).strip("-")
    return slug or "author"


@dataclass
class AuthorListItemData:
    id: int
    name_ar: str
    name_latin: str
    affiliation: str | None
    slug: str
    created_at: datetime
    deleted_at: datetime | None = None


@dataclass
class PaginatedAuthors:
    items: list[AuthorListItemData]
    total: int
    page: int
    page_size: int
    has_next: bool


class AuthorAdminRepository:
    """Administrative helpers for author management."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def list_authors(
        self,
        *,
        q: str | None,
        page: int,
        page_size: int,
        sort: Literal["name", "created_at"],
        status: Literal["active", "deleted", "all"],
    ) -> PaginatedAuthors:
        page = max(1, page)
        page_size = max(1, min(page_size, 50))

        filters = []
        if q:
            pattern = f"%{q.strip().lower()}%"
            filters.append(func.lower(func.coalesce(Author.full_name_lat, "")).like(pattern))
        if status == "active":
            filters.append(Author.deleted_at.is_(None))
        elif status == "deleted":
            filters.append(Author.deleted_at.is_not(None))

        base_stmt = select(Author)
        for clause in filters:
            base_stmt = base_stmt.where(clause)

        count_stmt = select(func.count()).select_from(Author)
        for clause in filters:
            count_stmt = count_stmt.where(clause)
        total = self._session.execute(count_stmt).scalar_one()

        if sort == "created_at":
            order_clause = (Author.created_at.desc(), Author.id.desc())
        else:
            order_clause = (
                func.lower(func.coalesce(Author.full_name_lat, "")),
                Author.id.asc(),
            )

        stmt = (
            base_stmt.order_by(*order_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self._session.execute(stmt).scalars().all()
        items = [self._serialize_author(row) for row in rows]
        has_next = page * page_size < total
        return PaginatedAuthors(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

    def create_author(self, payload: AuthorCreate) -> AuthorListItemData:
        name_latin = (payload.name_latin or "").strip()
        if not name_latin:
            raise AuthorAdminError("Latin name is required.", status_code=400)

        name_ar = (payload.name_ar or "").strip() or name_latin
        affiliation = (payload.affiliation or "").strip() or None
        slug = slugify_value(name_latin)
        self._assert_unique_slug(slug)

        author = Author(
            full_name_ar=name_ar,
            full_name_lat=name_latin,
            affiliation=affiliation,
            slug=slug,
        )
        self._session.add(author)
        self._session.flush()
        self._session.refresh(author)
        return self._serialize_author(author)

    def _assert_unique_slug(self, slug: str) -> None:
        exists = self._session.execute(select(Author.id).where(Author.slug == slug)).first()
        if exists:
            raise AuthorAdminError("An author with this name already exists.", status_code=409)

    @staticmethod
    def _serialize_author(author: Author) -> AuthorListItemData:
        return AuthorListItemData(
            id=author.id,
            name_ar=author.full_name_ar,
            name_latin=author.full_name_lat or "",
            affiliation=author.affiliation,
            slug=author.slug or "",
            created_at=author.created_at,
            deleted_at=author.deleted_at,
        )

    def soft_delete_author(self, author_id: int) -> None:
        stmt = (
            update(Author)
            .where(Author.id == author_id)
            .values(deleted_at=func.now())
            .execution_options(synchronize_session=False)
        )
        result = self._session.execute(stmt)
        self._session.expire_all()
        if result.rowcount == 0:
            raise AuthorAdminError("Author not found.", status_code=404)

    def restore_author(self, author_id: int) -> None:
        stmt = (
            update(Author)
            .where(Author.id == author_id)
            .values(deleted_at=None)
            .execution_options(synchronize_session=False)
        )
        result = self._session.execute(stmt)
        self._session.expire_all()
        if result.rowcount == 0:
            raise AuthorAdminError("Author not found.", status_code=404)


__all__ = ["AuthorAdminRepository", "AuthorAdminError", "AuthorListItemData", "PaginatedAuthors"]
