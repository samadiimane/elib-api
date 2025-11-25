from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, load_only, selectinload
from sqlalchemy.sql import ColumnElement

from app.models.author import Author
from app.models.category import Category, CategoryKind
from app.models.document import Document, DocumentType
from app.models.journal import Journal, JournalIssue
from app.repositories.documents import (
    DocumentRepository,
    build_base_filters,
    list_documents as list_documents_query,
)
from app.schemas.admin_document import AdminDocumentCreate, AdminDocumentUpdate


@dataclass
class AdminDocumentListResult:
    items: list[Document]
    total: int
    page: int
    page_size: int
    has_next: bool


class DocumentAdminError(Exception):
    """Domain error for admin document operations."""

    def __init__(self, user_message: str, *, status_code: int = 400) -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code


class AdminDocumentRepository:
    """Read-only admin operations for documents."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def _base_query(
        self,
        *,
        q: str | None,
        type_: DocumentType | Sequence[DocumentType] | None,
        lang: str | Sequence[str] | None,
        year_min: int | None,
        year_max: int | None,
        category_slug: str | None,
    ):
        base_query = build_base_filters(
            self._session,
            q=q,
            type_=type_,
            lang=lang,
            year_from=year_min,
            year_to=year_max,
            category_slug=category_slug,
            include_descendants=True,
            include_deleted=True,
        )
        return base_query.options(
            load_only(
                Document.id,
                Document.title,
                Document.type,
                Document.lang,
                Document.year,
                Document.pages,
                Document.primary_category_id,
                Document.journal_id,
                Document.issue_id,
                Document.created_at,
                Document.updated_at,
                Document.deleted_at,
                Document.start_page,
                Document.end_page,
                Document.doi,
                Document.isbn,
                Document.issn,
                Document.abstract,
                Document.cover_image_url,
            ),
            selectinload(Document.primary_category).load_only(
                Category.id,
                Category.slug,
                Category.name,
                Category.kind,
            ),
            selectinload(Document.journal).load_only(
                Journal.id,
                Journal.slug,
                Journal.name,
            ),
            selectinload(Document.issue).load_only(
                JournalIssue.id,
                JournalIssue.year,
                JournalIssue.volume,
                JournalIssue.number,
                JournalIssue.title,
            ),
            selectinload(Document.authors).load_only(
                Author.id,
                Author.full_name_ar,
                Author.full_name_lat,
            ),
        )

    def list_documents(
        self,
        *,
        q: str | None,
        type_: DocumentType | None,
        lang: str | None,
        year_min: int | None,
        year_max: int | None,
        category_slug: str | None,
        journal_id: int | None,
        issue_id: int | None,
        status: Literal["active", "deleted", "all"],
        sort_clause: ColumnElement,
        page: int,
        page_size: int,
    ) -> AdminDocumentListResult:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        base_query = self._base_query(
            q=q,
            type_=type_,
            lang=lang,
            year_min=year_min,
            year_max=year_max,
            category_slug=category_slug,
        )

        if journal_id is not None:
            base_query = base_query.where(Document.journal_id == journal_id)
        if issue_id is not None:
            base_query = base_query.where(Document.issue_id == issue_id)

        if status == "active":
            base_query = base_query.where(Document.deleted_at.is_(None))
        elif status == "deleted":
            base_query = base_query.where(Document.deleted_at.is_not(None))

        items, total = list_documents_query(
            self._session,
            base_query,
            sort_clause=sort_clause,
            page=page,
            page_size=page_size,
        )
        has_next = (page - 1) * page_size + len(items) < (total or 0)
        return AdminDocumentListResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

    def get_document(self, document_id: int) -> Document | None:
        stmt = (
            select(Document)
            .options(
                load_only(
                    Document.id,
                    Document.title,
                    Document.type,
                    Document.lang,
                    Document.year,
                    Document.pages,
                    Document.primary_category_id,
                    Document.journal_id,
                    Document.issue_id,
                    Document.created_at,
                    Document.updated_at,
                    Document.start_page,
                    Document.end_page,
                    Document.doi,
                    Document.isbn,
                    Document.issn,
                    Document.abstract,
                    Document.cover_image_url,
                ),
                selectinload(Document.primary_category).load_only(
                    Category.id,
                    Category.slug,
                    Category.name,
                    Category.kind,
                ),
                selectinload(Document.journal).load_only(
                    Journal.id,
                    Journal.slug,
                    Journal.name,
                ),
                selectinload(Document.issue).load_only(
                    JournalIssue.id,
                    JournalIssue.year,
                    JournalIssue.volume,
                    JournalIssue.number,
                    JournalIssue.title,
                ),
                selectinload(Document.authors).load_only(
                    Author.id,
                    Author.full_name_ar,
                    Author.full_name_lat,
                ),
            )
            .where(Document.id == document_id)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    # -----------------------------
    # Mutations
    # -----------------------------

    def create_document(self, payload: AdminDocumentCreate) -> Document:
        data = payload.model_dump()
        normalized = self._normalize_payload(data)
        document = Document(
            title=normalized["title"],
            abstract=normalized["abstract"],
            type=normalized["type"],
            lang=normalized["lang"],
            year=normalized["year"],
            pages=normalized["pages"],
            doi=normalized["doi"],
            isbn=normalized["isbn"],
            issn=normalized["issn"],
            primary_category_id=normalized["primary_category_id"],
            journal_id=normalized["journal_id"],
            issue_id=normalized["issue_id"],
            cover_image_url=normalized["cover_image_url"],
            start_page=normalized["start_page"],
            end_page=normalized["end_page"],
            file_key=normalized["file_key"],
        )
        self._session.add(document)
        self._session.flush()

        if normalized["author_ids"]:
            DocumentRepository(self._session).assign_authors(document, normalized["author_ids"])

        self._session.flush()
        self._session.refresh(document)
        return document

    def update_document(self, document_id: int, payload: AdminDocumentUpdate) -> Document:
        document = self._session.get(Document, document_id)
        if document is None:
            raise DocumentAdminError("Document not found.", status_code=404)

        incoming = payload.model_dump(exclude_unset=True)
        normalized = self._normalize_payload(incoming, existing=document)

        if "title" in incoming:
            document.title = normalized["title"]
        if "abstract" in incoming:
            document.abstract = normalized["abstract"]
        document.type = normalized["type"]
        if "lang" in incoming:
            document.lang = normalized["lang"]
        document.year = normalized["year"]
        document.pages = normalized["pages"]
        document.doi = normalized["doi"]
        document.isbn = normalized["isbn"]
        document.issn = normalized["issn"]
        document.primary_category_id = normalized["primary_category_id"]
        document.journal_id = normalized["journal_id"]
        document.issue_id = normalized["issue_id"]
        document.cover_image_url = normalized["cover_image_url"]
        document.start_page = normalized["start_page"]
        document.end_page = normalized["end_page"]
        document.file_key = normalized["file_key"]

        if normalized["author_ids"] is not None:
            DocumentRepository(self._session).assign_authors(document, normalized["author_ids"])

        self._session.flush()
        self._session.refresh(document)
        return document

    def soft_delete_document(self, document_id: int) -> Document:
        document = self._session.get(Document, document_id)
        if document is None:
            raise DocumentAdminError("Document not found.", status_code=404)
        if document.deleted_at is None:
            document.deleted_at = datetime.now(timezone.utc)
        self._session.flush()
        self._session.refresh(document)
        return document

    def restore_document(self, document_id: int) -> Document:
        document = self._session.get(Document, document_id)
        if document is None:
            raise DocumentAdminError("Document not found.", status_code=404)
        document.deleted_at = None
        self._session.flush()
        self._session.refresh(document)
        return document

    # -----------------------------
    # Helpers
    # -----------------------------

    def _normalize_payload(self, data: dict, existing: Document | None = None) -> dict:
        """Validate invariants and normalize values."""
        title = data.get("title", existing.title if existing else None)
        if not title:
            raise DocumentAdminError("Title is required.", status_code=422)

        lang = data.get("lang", existing.lang if existing else None)
        if not lang:
            raise DocumentAdminError("Language is required.", status_code=422)

        journal_id = data.get("journal_id", existing.journal_id if existing else None)
        issue_id = data.get("issue_id", existing.issue_id if existing else None)
        category_id = data.get("primary_category_id", existing.primary_category_id if existing else None)
        category = None
        if category_id is not None:
            category = self._session.get(Category, category_id)
            if category is None:
                raise DocumentAdminError("Category not found.", status_code=422)

        issue = None
        if issue_id is not None:
            issue = self._session.get(JournalIssue, issue_id)
            if issue is None:
                raise DocumentAdminError("Issue not found.", status_code=404)
            journal_id = issue.journal_id

        journal = None
        if journal_id is not None:
            journal = self._session.get(Journal, journal_id)
            if journal is None:
                raise DocumentAdminError("Journal not found.", status_code=404)

        doc_type = data.get("type", existing.type if existing else None)
        if isinstance(doc_type, str):
            try:
                doc_type = DocumentType(doc_type)
            except ValueError:
                raise DocumentAdminError("Unsupported document type.", status_code=422)

        if issue_id is not None:
            doc_type = DocumentType.article

        if journal_id is not None and category and category.kind == CategoryKind.journal and issue_id is None:
            doc_type = DocumentType.article

        if category and category.kind == CategoryKind.archive_collection:
            doc_type = DocumentType.archive_item

        if category and category.slug == "historical-sites" and doc_type is None:
            doc_type = DocumentType.site_record

        if doc_type is None:
            doc_type = DocumentType.other

        year = data.get("year", existing.year if existing else None)
        if year is not None and not (1800 <= year <= 2100):
            raise DocumentAdminError("Year must be between 1800 and 2100.", status_code=422)

        start_page = data.get("start_page", existing.start_page if existing else None)
        end_page = data.get("end_page", existing.end_page if existing else None)
        pages = data.get("pages", existing.pages if existing else None)

        if start_page is not None and end_page is not None:
            if end_page < start_page:
                raise DocumentAdminError("End page cannot be before start page.", status_code=422)
            if pages is None:
                pages = (end_page - start_page) + 1

        if pages is not None and pages < 0:
            raise DocumentAdminError("Pages must be zero or a positive number.", status_code=422)

        author_ids = None
        if "author_ids" in data:
            raw_ids = data.get("author_ids") or []
            deduped: list[int] = []
            seen: set[int] = set()
            for raw in raw_ids:
                try:
                    value = int(raw)
                except (TypeError, ValueError):
                    continue
                if value in seen:
                    continue
                deduped.append(value)
                seen.add(value)

            if deduped:
                authors = self._session.execute(
                    select(Author).where(Author.id.in_(deduped), Author.deleted_at.is_(None))
                ).scalars().all()
                found_ids = {author.id for author in authors}
                missing = [aid for aid in deduped if aid not in found_ids]
                if missing:
                    raise DocumentAdminError("One or more authors are missing or inactive.", status_code=422)
            author_ids = deduped

        return {
            "title": title,
            "abstract": data.get("abstract", existing.abstract if existing else None),
            "type": doc_type,
            "lang": lang,
            "year": year,
            "pages": pages,
            "doi": data.get("doi", existing.doi if existing else None),
            "isbn": data.get("isbn", existing.isbn if existing else None),
            "issn": data.get("issn", existing.issn if existing else None),
            "primary_category_id": category_id,
            "journal_id": journal_id,
            "issue_id": issue_id,
            "cover_image_url": data.get("cover_image_url", existing.cover_image_url if existing else None),
            "start_page": start_page,
            "end_page": end_page,
            "author_ids": author_ids,
            "file_key": data.get("file_key", existing.file_key if existing else None),
        }


__all__ = ["AdminDocumentRepository", "AdminDocumentListResult"]
