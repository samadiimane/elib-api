from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, load_only

from app.models.document import Document, DocumentType
from app.models.journal import Journal, JournalIssue
from app.schemas.admin_journal import JournalCreate, JournalUpdate
from app.schemas.admin_issue import (
    AdminIssueListItemOut,
    AdminIssueListResponse,
    AdminIssueCreate,
    AdminIssueUpdate,
)


class JournalAdminError(Exception):
    """Domain error for admin journal operations."""

    def __init__(self, user_message: str, *, status_code: int = 400, code: str = "JOURNAL_ERROR") -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code
        self.code = code


SlugPattern = re.compile(r"[^a-z0-9]+")


def slugify_value(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = SlugPattern.sub("-", ascii_value.lower()).strip("-")
    return slug or "journal"


@dataclass
class JournalListItemData:
    id: int
    name: str
    slug: str
    issn: str | None
    description: str | None
    publisher: str | None
    cover_image_url: str | None
    created_at: datetime
    deleted_at: datetime | None
    issues_count: int
    articles_count: int


@dataclass
class PaginatedJournals:
    items: list[JournalListItemData]
    total: int
    page: int
    page_size: int
    has_next: bool


class JournalAdminRepository:
    """Administrative helpers for managing journals."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def list_journals(
        self,
        *,
        q: str | None,
        status: Literal["active", "deleted", "all"],
        page: int,
        page_size: int,
        sort: Literal["name", "created_at"],
    ) -> PaginatedJournals:
        page = max(1, page)
        page_size = max(1, min(page_size, 50))

        filters = []
        if q:
            pattern = f"%{q.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(Journal.name).like(pattern),
                    func.lower(Journal.slug).like(pattern),
                )
            )
        if status == "active":
            filters.append(Journal.deleted_at.is_(None))
        elif status == "deleted":
            filters.append(Journal.deleted_at.is_not(None))

        issues_count_subquery = (
            select(func.count(JournalIssue.id))
            .where(JournalIssue.journal_id == Journal.id)
            .correlate(Journal)
            .scalar_subquery()
        )
        articles_count_subquery = (
            select(func.count(Document.id))
            .where(Document.journal_id == Journal.id)
            .where(Document.type == DocumentType.article)
            .correlate(Journal)
            .scalar_subquery()
        )

        stmt = (
            select(
                Journal,
                issues_count_subquery.label("issues_count"),
                articles_count_subquery.label("articles_count"),
            )
            .options(
                load_only(
                    Journal.id,
                    Journal.name,
                    Journal.slug,
                    Journal.issn,
                    Journal.publisher,
                    Journal.description,
                    Journal.cover_image_url,
                    Journal.created_at,
                    Journal.deleted_at,
                )
            )
        )

        for clause in filters:
            stmt = stmt.where(clause)

        if sort == "created_at":
            order_by = (Journal.created_at.desc(), Journal.id.desc())
        else:
            order_by = (func.lower(Journal.name).asc(), Journal.id.asc())

        stmt = (
            stmt.order_by(*order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        count_stmt = select(func.count(Journal.id))
        for clause in filters:
            count_stmt = count_stmt.where(clause)
        total = self._session.execute(count_stmt).scalar_one()

        rows = self._session.execute(stmt).all()
        items = [
            self._serialize_list_item(
                row[0],
                issues_count=row.issues_count or 0,
                articles_count=row.articles_count or 0,
            )
            for row in rows
        ]
        has_next = page * page_size < total
        return PaginatedJournals(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

    def create_journal(self, payload: JournalCreate) -> JournalListItemData:
        name = payload.name.strip()
        if not name:
            raise JournalAdminError(
                "Name is required.",
                status_code=400,
                code="JOURNAL_NAME_REQUIRED",
            )

        slug_source = (payload.slug or name).strip()
        if not slug_source:
            raise JournalAdminError(
                "Slug is required.",
                status_code=400,
                code="JOURNAL_SLUG_REQUIRED",
            )

        slug = slugify_value(slug_source)
        self._assert_unique_active_slug(slug)

        journal = Journal(
            name=name,
            slug=slug,
            issn=_normalize_optional(payload.issn),
            description=_normalize_optional(payload.description),
            publisher=_normalize_optional(payload.publisher),
            cover_image_url=_normalize_optional(payload.cover_image_url),
        )
        self._session.add(journal)
        self._session.flush()
        self._session.refresh(journal)

        issues_count, articles_count = self._count_relations(journal.id)
        return self._serialize_list_item(journal, issues_count, articles_count)

    def update_journal(self, journal_id: int, payload: JournalUpdate) -> JournalListItemData:
        journal = self._session.get(Journal, journal_id)
        if journal is None:
            raise JournalAdminError("Journal not found.", status_code=404, code="JOURNAL_NOT_FOUND")

        if payload.name is not None:
            name = payload.name.strip()
            if not name:
                raise JournalAdminError(
                    "Name cannot be empty.",
                    status_code=400,
                    code="JOURNAL_NAME_REQUIRED",
                )
            journal.name = name

        if payload.slug is not None:
            slug_source = payload.slug.strip()
            if not slug_source:
                raise JournalAdminError(
                    "Slug cannot be empty.",
                    status_code=400,
                    code="JOURNAL_SLUG_REQUIRED",
                )
            normalized_slug = slugify_value(slug_source)
            if normalized_slug != journal.slug:
                self._assert_unique_active_slug(normalized_slug, exclude_id=journal.id)
                journal.slug = normalized_slug

        if payload.issn is not None:
            journal.issn = _normalize_optional(payload.issn)
        if payload.description is not None:
            journal.description = _normalize_optional(payload.description)
        if payload.publisher is not None:
            journal.publisher = _normalize_optional(payload.publisher)
        if payload.cover_image_url is not None:
            journal.cover_image_url = _normalize_optional(payload.cover_image_url)

        self._session.flush()
        self._session.refresh(journal)
        issues_count, articles_count = self._count_relations(journal.id)
        return self._serialize_list_item(journal, issues_count, articles_count)

    def soft_delete(self, journal_id: int) -> None:
        stmt = (
            update(Journal)
            .where(Journal.id == journal_id)
            .values(deleted_at=func.now())
            .execution_options(synchronize_session=False)
        )
        result = self._session.execute(stmt)
        self._session.expire_all()
        if result.rowcount == 0:
            raise JournalAdminError("Journal not found.", status_code=404, code="JOURNAL_NOT_FOUND")

    def restore(self, journal_id: int) -> None:
        stmt = (
            update(Journal)
            .where(Journal.id == journal_id)
            .values(deleted_at=None)
            .execution_options(synchronize_session=False)
        )
        result = self._session.execute(stmt)
        self._session.expire_all()
        if result.rowcount == 0:
            raise JournalAdminError("Journal not found.", status_code=404, code="JOURNAL_NOT_FOUND")

    def list_issues(
        self,
        journal_id: int,
        *,
        q: str | None,
        year: int | None,
        page: int,
        page_size: int,
        sort: Literal["year_desc", "year_asc", "number_desc", "number_asc", "created_desc", "created_asc"],
    ) -> AdminIssueListResponse:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        filters = [JournalIssue.journal_id == journal_id]
        if q:
            pattern = f"%{q.strip()}%"
            filters.append(JournalIssue.title.ilike(pattern))
        if year is not None:
            filters.append(JournalIssue.year == year)

        order_by = {
            "year_desc": (JournalIssue.year.desc(), JournalIssue.id.desc()),
            "year_asc": (JournalIssue.year.asc(), JournalIssue.id.asc()),
            "number_desc": (JournalIssue.number.desc().nulls_last(), JournalIssue.id.desc()),
            "number_asc": (JournalIssue.number.asc().nulls_last(), JournalIssue.id.asc()),
            "created_desc": (JournalIssue.id.desc(),),
            "created_asc": (JournalIssue.id.asc(),),
        }.get(sort, (JournalIssue.year.desc(), JournalIssue.id.desc()))

        articles_count_subquery = (
            select(func.count(Document.id))
            .where(Document.issue_id == JournalIssue.id)
            .where(Document.type == DocumentType.article)
            .correlate(JournalIssue)
            .scalar_subquery()
        )

        stmt = (
            select(
                JournalIssue.id,
                JournalIssue.journal_id,
                JournalIssue.volume,
                JournalIssue.number,
                JournalIssue.year,
                JournalIssue.title,
                JournalIssue.issue_date,
                articles_count_subquery.label("articles_count"),
            )
            .where(*filters)
            .order_by(*order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        total_stmt = select(func.count()).select_from(JournalIssue).where(*filters)
        total = self._session.execute(total_stmt).scalar_one()

        rows = self._session.execute(stmt).all()
        items = [
            AdminIssueListItemOut(
                id=row.id,
                journal_id=row.journal_id,
                volume=row.volume,
                number=row.number,
                year=row.year,
                title=row.title,
                cover_image_url=None,
                published_at=row.issue_date,
                articles_count=row.articles_count or 0,
                created_at=None,
            )
            for row in rows
        ]
        has_next = page * page_size < (total or 0)
        return AdminIssueListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

    def create_issue(self, journal_id: int, payload: AdminIssueCreate) -> AdminIssueListItemOut:
        self._validate_issue_payload(payload)
        self._assert_issue_unique(journal_id, payload.year, payload.number)

        issue = JournalIssue(
            journal_id=journal_id,
            title=_normalize_optional(payload.title),
            year=payload.year,
            number=payload.number,
            volume=payload.volume,
            issue_date=payload.published_at,
        )
        self._session.add(issue)
        self._session.flush()
        self._session.refresh(issue)
        articles_count = self._issue_articles_count(issue.id)
        return self._serialize_issue(issue, articles_count)

    def update_issue(self, issue_id: int, patch: AdminIssueUpdate) -> AdminIssueListItemOut:
        issue = self._session.get(JournalIssue, issue_id)
        if issue is None:
            raise JournalAdminError("Issue not found.", status_code=404, code="ISSUE_NOT_FOUND")

        self._validate_issue_payload(patch)

        if patch.year is not None:
            issue.year = patch.year
        if patch.number is not None:
            issue.number = patch.number
        if patch.volume is not None:
            issue.volume = patch.volume
        if patch.title is not None:
            issue.title = _normalize_optional(patch.title)
        if patch.published_at is not None:
            issue.issue_date = patch.published_at

        if issue.year is not None and issue.number is not None:
            self._assert_issue_unique(issue.journal_id, issue.year, issue.number, exclude_id=issue.id)

        self._session.flush()
        self._session.refresh(issue)
        articles_count = self._issue_articles_count(issue.id)
        return self._serialize_issue(issue, articles_count)

    def delete_issue(self, issue_id: int) -> None:
        issue = self._session.get(JournalIssue, issue_id)
        if issue is None:
            raise JournalAdminError("Issue not found.", status_code=404, code="ISSUE_NOT_FOUND")

        articles_count = self._issue_articles_count(issue.id)
        if articles_count > 0:
            raise JournalAdminError(
                "Cannot delete an issue that has articles.",
                status_code=409,
                code="ISSUE_HAS_ARTICLES",
            )

        self._session.delete(issue)
        self._session.flush()

    # -----------------------
    # Helpers
    # -----------------------

    def _issue_articles_count(self, issue_id: int) -> int:
        return (
            self._session.execute(
                select(func.count(Document.id)).where(
                    Document.issue_id == issue_id, Document.type == DocumentType.article
                )
            ).scalar_one()
            or 0
        )

    def _serialize_issue(self, issue: JournalIssue, articles_count: int) -> AdminIssueListItemOut:
        return AdminIssueListItemOut(
            id=issue.id,
            journal_id=issue.journal_id,
            volume=issue.volume,
            number=issue.number,
            year=issue.year,
            title=issue.title,
            cover_image_url=None,
            published_at=issue.issue_date,
            articles_count=articles_count,
            created_at=None,
        )

    def _validate_issue_payload(self, payload: AdminIssueCreate | AdminIssueUpdate) -> None:
        if payload.year is not None and not (1800 <= payload.year <= 2100):
            raise JournalAdminError("Year must be between 1800 and 2100.", status_code=400, code="INVALID_YEAR")
        for field_name in ("number", "volume"):
            value = getattr(payload, field_name, None)
            if value is not None and value < 0:
                raise JournalAdminError(f"{field_name.capitalize()} must be non-negative.", status_code=400, code="INVALID_NUMBER")

    def _assert_issue_unique(
        self,
        journal_id: int,
        year: int | None,
        number: int | None,
        *,
        exclude_id: int | None = None,
    ) -> None:
        if year is None or number is None:
            return
        stmt = select(JournalIssue.id).where(
            JournalIssue.journal_id == journal_id,
            JournalIssue.year == year,
            JournalIssue.number == number,
        )
        if exclude_id is not None:
            stmt = stmt.where(JournalIssue.id != exclude_id)
        exists = self._session.execute(stmt.limit(1)).scalar_one_or_none()
        if exists is not None:
            raise JournalAdminError(
                "An issue with this year and number already exists.",
                status_code=409,
                code="ISSUE_DUPLICATE",
            )

    def _serialize_list_item(
        self,
        journal: Journal,
        issues_count: int,
        articles_count: int,
    ) -> JournalListItemData:
        return JournalListItemData(
            id=journal.id,
            name=journal.name,
            slug=journal.slug,
            issn=journal.issn,
            description=journal.description,
            cover_image_url=journal.cover_image_url,
            created_at=journal.created_at,
            deleted_at=journal.deleted_at,
            issues_count=issues_count,
            articles_count=articles_count,
            publisher=journal.publisher,
        )

    def _assert_unique_active_slug(self, slug: str, *, exclude_id: int | None = None) -> None:
        stmt = select(Journal.id).where(Journal.slug == slug, Journal.deleted_at.is_(None))
        if exclude_id is not None:
            stmt = stmt.where(Journal.id != exclude_id)
        exists = self._session.execute(stmt.limit(1)).scalar_one_or_none()
        if exists is not None:
            raise JournalAdminError(
                "A journal with this slug already exists.",
                status_code=409,
                code="JOURNAL_SLUG_EXISTS",
            )

    def _count_relations(self, journal_id: int) -> tuple[int, int]:
        issues_count = self._session.execute(
            select(func.count(JournalIssue.id)).where(JournalIssue.journal_id == journal_id)
        ).scalar_one()
        articles_count = self._session.execute(
            select(func.count(Document.id)).where(
                Document.journal_id == journal_id,
                Document.type == DocumentType.article,
            )
        ).scalar_one()
        return issues_count or 0, articles_count or 0


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


__all__ = [
    "JournalAdminRepository",
    "JournalAdminError",
    "JournalListItemData",
    "PaginatedJournals",
    "slugify_value",
]
