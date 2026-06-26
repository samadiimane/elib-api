"""Seed Dar al-Niaba issue 12 articles.

Usage:
    python -m scripts.seed_dar_al_niaba_issue_12
    python -m scripts.seed_dar_al_niaba_issue_12 dar-al-niaba-12-3

The optional arguments are doc ids derived from file_key basenames.
"""

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


ISSUE = {
    "journal_slug": "dar-al-niaba",
    "journal_name": "Dar al-Niaba",
    "title": "العدد الثاني عشر، السنة الثالثة، خريف 1986",
    "year": 1986,
    "volume": 3,
    "number": 12,
}


ARTICLES = [
    {
        "title": "افتتاحية",
        "authors": [],
        "lang": "ar",
        "pages": 7,
        "start_page": 1,
        "end_page": 5,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-1.pdf",
    },
    {
        "title": "هل آن الأوان لبعث تاريخ المقاومة المغربية خلال القرن العشرين؟",
        "authors": ["محمد المنوني"],
        "lang": "ar",
        "pages": 3,
        "start_page": 27,
        "end_page": 29,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-3.pdf",
    },
    {
        "title": "أسماء مغمورة لقادة الجهاد في المغرب: القائد أحمد تازية الوهابي",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 4,
        "start_page": 30,
        "end_page": 33,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-4.pdf",
    },
    {
        "title": "محمد الخامس : عرش وثلاث جمهوريات",
        "authors": ["مصطفى بوشعراء"],
        "lang": "ar",
        "pages": 6,
        "start_page": 34,
        "end_page": 39,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-5.pdf",
    },
    {
        "title": "قضية مقتل الفرنسي شاربونيي بطنجة من خلال الوثائق المغربية (27 ماي 1906)",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 40,
        "end_page": 41,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-6.pdf",
    },
    {
        "title": "مخطوط جديد حول هدية الفيل من الملكة فكتوريا إلى السلطان مولاي الحسن",
        "authors": ["خالد بن الصغير"],
        "lang": "ar",
        "pages": 5,
        "start_page": 44,
        "end_page": 48,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-7.pdf",
    },
    {
        "title": "وثيقة جديدة حول العلاقات المغربية الإنجليزية : الرحلة لجبل طارق لمقابلة سلطان الانجليز سنة 1321 ه",
        "authors": ["عبد العزيز التمسماني خلوق"],
        "lang": "ar",
        "pages": 2,
        "start_page": 49,
        "end_page": 50,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-8.pdf",
    },
    {
        "title": "الحج المغربي إلى الديار المقدسة في القرن 19 وبداية القرن العشرين",
        "authors": ["محمد الأمين البزاز"],
        "lang": "ar",
        "pages": 11,
        "start_page": 51,
        "end_page": 61,
        "file_key": "dar-al-niaba/pdf/dar-al-niaba-12-9.pdf",
    },
]


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


def get_or_create_journal(session) -> Journal:
    journal = session.execute(
        select(Journal)
        .where(Journal.slug == ISSUE["journal_slug"])
        .where(Journal.deleted_at.is_(None))
        .order_by(Journal.id.asc())
    ).scalars().first()
    if journal is not None:
        return journal

    journal = Journal(slug=ISSUE["journal_slug"], name=ISSUE["journal_name"])
    session.add(journal)
    session.flush()
    return journal


def get_or_create_journal_category(session, journal: Journal) -> Category:
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
            order_index=ISSUE["number"],
        )
        session.add(category)
        session.flush()
        return category

    category.name = journal.name
    category.parent = journals_parent
    category.journal = journal
    session.flush()
    return category


def get_or_create_issue(session, journal: Journal) -> JournalIssue:
    issue = session.execute(
        select(JournalIssue)
        .where(JournalIssue.journal_id == journal.id)
        .where(JournalIssue.year == ISSUE["year"])
        .where(JournalIssue.volume == ISSUE["volume"])
        .where(JournalIssue.number == ISSUE["number"])
    ).scalar_one_or_none()
    if issue is None:
        issue = JournalIssue(
            journal=journal,
            year=ISSUE["year"],
            volume=ISSUE["volume"],
            number=ISSUE["number"],
            title=ISSUE["title"],
        )
        session.add(issue)
        session.flush()
        return issue

    issue.title = ISSUE["title"]
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
    document.year = ISSUE["year"]
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


def _selected_articles(doc_ids: Sequence[str]) -> list[dict]:
    if not doc_ids:
        return ARTICLES

    by_doc_id = {_article_doc_id(article): article for article in ARTICLES}
    missing = [doc_id for doc_id in doc_ids if doc_id not in by_doc_id]
    if missing:
        raise SystemExit(f"Unknown doc_id(s): {', '.join(missing)}")
    return [by_doc_id[doc_id] for doc_id in doc_ids]


def run(doc_ids: Sequence[str] = ()) -> None:
    session = SessionLocal()
    try:
        journal = get_or_create_journal(session)
        category = get_or_create_journal_category(session, journal)
        issue = get_or_create_issue(session, journal)

        articles = _selected_articles(doc_ids)
        for article in articles:
            upsert_article(session, journal=journal, issue=issue, category=category, payload=article)

        session.commit()
        print(
            f"Seeded Dar al-Niaba issue {ISSUE['number']:02d} "
            f"articles: {len(articles)}"
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run(sys.argv[1:])
