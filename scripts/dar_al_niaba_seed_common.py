from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Author,
    Category,
    CategoryKind,
    Document,
    DocumentAuthor,
    DocumentType,
    Journal,
    JournalIssue,
)

configure_mappers()


def _set_if_exists(obj: object, attr: str, value: object) -> None:
    if hasattr(obj, attr):
        setattr(obj, attr, value)


def _stable_author_slug(full_name_ar: str) -> str:
    digest = hashlib.sha1(full_name_ar.encode("utf-8")).hexdigest()[:12]
    return f"dar-al-niaba-author-{digest}"


def _article_doc_id(article: dict) -> str:
    return Path(article["file_key"]).stem


def get_category(session, slug: str, kind: CategoryKind) -> Category | None:
    return session.execute(
        select(Category)
        .where(Category.slug == slug)
        .where(Category.kind == kind)
        .order_by(Category.id.asc())
    ).scalars().first()


def get_or_create_journal(session, issue_config: dict) -> Journal:
    journal = session.execute(
        select(Journal)
        .where(Journal.slug == issue_config["journal_slug"])
        .where(Journal.deleted_at.is_(None))
        .order_by(Journal.id.asc())
    ).scalars().first()
    if journal is not None:
        return journal

    journal = Journal(slug=issue_config["journal_slug"], name=issue_config["journal_name"])
    session.add(journal)
    session.flush()
    return journal


def get_or_create_journal_category(session, journal: Journal, issue_config: dict) -> Category:
    journals_parent = get_category(session, "journals", CategoryKind.section)
    if journals_parent is None:
        journals_parent = Category(
            slug="journals",
            name="Journals",
            kind=CategoryKind.section,
            order_index=2,
        )
        session.add(journals_parent)
        session.flush()

    category = get_category(session, journal.slug, CategoryKind.journal)
    if category is None:
        category = Category(
            slug=journal.slug,
            name=journal.name,
            kind=CategoryKind.journal,
            parent=journals_parent,
            journal=journal,
            order_index=issue_config["number"],
        )
        session.add(category)
        session.flush()
        return category

    category.name = journal.name
    category.parent = journals_parent
    category.journal = journal
    session.flush()
    return category


def get_or_create_issue(session, journal: Journal, issue_config: dict) -> JournalIssue:
    issue = session.execute(
        select(JournalIssue)
        .where(JournalIssue.journal_id == journal.id)
        .where(JournalIssue.year == issue_config["year"])
        .where(JournalIssue.volume == issue_config["volume"])
        .where(JournalIssue.number == issue_config["number"])
    ).scalar_one_or_none()
    if issue is None:
        issue = JournalIssue(
            journal=journal,
            year=issue_config["year"],
            volume=issue_config["volume"],
            number=issue_config["number"],
            title=issue_config["title"],
        )
        session.add(issue)
        session.flush()
        return issue

    issue.title = issue_config["title"]
    return issue


def get_or_create_author(session, full_name_ar: str) -> Author:
    author = session.execute(
        select(Author)
        .where(Author.full_name_ar == full_name_ar)
        .order_by(Author.id.asc())
    ).scalars().first()
    if author is not None:
        _set_if_exists(author, "deleted_at", None)
        return author

    slug = _stable_author_slug(full_name_ar)
    author = session.execute(select(Author).where(Author.slug == slug)).scalar_one_or_none()
    if author is not None:
        _set_if_exists(author, "deleted_at", None)
        author.full_name_ar = full_name_ar
        return author

    author = Author(full_name_ar=full_name_ar, slug=slug)
    session.add(author)
    session.flush()
    return author


def set_document_authors(document: Document, authors: Sequence[Author]) -> None:
    existing = {link.author_id: link for link in document.author_links}
    desired_ids: set[int] = set()

    for position, author in enumerate(authors, start=1):
        desired_ids.add(author.id)
        link = existing.get(author.id)
        if link is None:
            document.author_links.append(DocumentAuthor(author_id=author.id, position=position))
        else:
            link.position = position

    for link in list(document.author_links):
        if link.author_id not in desired_ids:
            document.author_links.remove(link)


def upsert_article(
    session,
    *,
    journal: Journal,
    issue: JournalIssue,
    category: Category | None,
    issue_config: dict,
    payload: dict,
) -> Document:
    document = session.execute(
        select(Document)
        .where(Document.file_key == payload["file_key"])
        .order_by(Document.id.asc())
    ).scalars().first()

    if document is None:
        document = Document(
            title=payload["title"],
            type=DocumentType.article,
            lang=payload["lang"],
            file_key=payload["file_key"],
        )
        session.add(document)
        session.flush()

    document.title = payload["title"]
    document.abstract = None
    document.type = DocumentType.article
    document.lang = payload["lang"]
    document.year = issue_config["year"]
    document.pages = payload["pages"]
    document.file_key = payload["file_key"]
    document.journal = journal
    document.issue = issue
    document.primary_category = category
    document.start_page = payload["start_page"]
    document.end_page = payload["end_page"]
    _set_if_exists(document, "deleted_at", None)

    authors = [get_or_create_author(session, name) for name in payload["authors"]]
    set_document_authors(document, authors)
    session.flush()
    return document


def selected_articles(articles: Sequence[dict], doc_ids: Sequence[str]) -> list[dict]:
    if not doc_ids:
        return list(articles)

    by_doc_id = {_article_doc_id(article): article for article in articles}
    missing = [doc_id for doc_id in doc_ids if doc_id not in by_doc_id]
    if missing:
        raise SystemExit(f"Unknown doc_id(s): {', '.join(missing)}")
    return [by_doc_id[doc_id] for doc_id in doc_ids]


def run_issue(issue_config: dict, articles_config: Sequence[dict], doc_ids: Sequence[str] = ()) -> None:
    session = SessionLocal()
    try:
        journal = get_or_create_journal(session, issue_config)
        category = get_or_create_journal_category(session, journal, issue_config)
        issue = get_or_create_issue(session, journal, issue_config)

        articles = selected_articles(articles_config, doc_ids)
        for article in articles:
            upsert_article(
                session,
                journal=journal,
                issue=issue,
                category=category,
                issue_config=issue_config,
                payload=article,
            )

        session.commit()
        print(
            f"Seeded Dar al-Niaba issue {issue_config['number']:02d} "
            f"articles: {len(articles)}"
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
