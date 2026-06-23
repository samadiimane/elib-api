"""Seed production navigation, journals, authors, documents, and translations."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import sqlalchemy as sa
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
)

configure_mappers()

# ============================================================
# Production seed data - Fondation AKT
# ============================================================

SECTIONS = [
{
"slug": "library",
"name": "Library",
"kind": CategoryKind.section,
"description": None,
"parent_slug": None,
"order_index": 1,
},
{
"slug": "journals",
"name": "Journals",
"kind": CategoryKind.section,
"description": None,
"parent_slug": None,
"order_index": 2,
},
{
"slug": "archives",
"name": "Archives & Documentary Heritage",
"kind": CategoryKind.section,
"description": None,
"parent_slug": None,
"order_index": 3,
},
{
"slug": "historical-sites",
"name": "Historical Sites & Landmarks",
"kind": CategoryKind.section,
"description": None,
"parent_slug": None,
"order_index": 4,
},
{
"slug": "research-themes",
"name": "Research Issues & Problematics",
"kind": CategoryKind.section,
"description": None,
"parent_slug": None,
"order_index": 5,
},
{
"slug": "publications",
"name": "Publications",
"kind": CategoryKind.section,
"description": None,
"parent_slug": None,
"order_index": 6,
},
]

SUBCATEGORIES = [
{
"slug": "manuscript",
"name": "Guide to Manuscript Collections",
"kind": CategoryKind.archive_collection,
"description": None,
"parent_slug": "archives",
"order_index": 1,
},
]

JOURNALS = [
{
"slug": "dar-al-niaba",
"name": "Dar al-Niaba",
"issn": None,
"publisher": "مؤسسة عبد العزيز خلوق التمسماني",
"description": None,
"cover_image_url": None,
"category_description": None,
"order_index": 1,
},
{
"slug": "les-tangerois",
"name": "Les Tangérois",
"issn": None,
"publisher": "مؤسسة عبد العزيز خلوق التمسماني",
"description": None,
"cover_image_url": None,
"category_description": None,
"order_index": 2,
},
]

AUTHORS = [
{
"slug": "abdelaziz-khallouk-temsamani",
"full_name_ar": "عبد العزيز خلوق التمسماني",
"full_name_lat": "Abdelaziz Khallouk Temsamani",
"affiliation": None,
},
{
"slug": "germain-ayache",
"full_name_ar": "جرمان عياش",
"full_name_lat": "Germain Ayache",
"affiliation": None,
},
{
"slug": "khalid-slaiki",
"full_name_ar": "خالد سليكي",
"full_name_lat": "Khalid Slaiki",
"affiliation": None,
},
{
"slug": "oussama-ezzekari",
"full_name_ar": "أسامة الزكاري",
"full_name_lat": "Oussama Ezzekari",
"affiliation": None,
},
{
"slug": "zoubida-ben-ali-ouriaghli",
"full_name_ar": "زبيدة الورياغلي",
"full_name_lat": "Zoubida Ben Ali Ouriaghli",
"affiliation": None,
},
{
"slug": "mustapha-el-ghachi",
"full_name_ar": "مصطفى الغاشي",
"full_name_lat": "Mustapha El Ghachi",
"affiliation": None,
},
{
"slug": "abdelatif-chahboun",
"full_name_ar": "عبد اللطيف شهبون",
"full_name_lat": "Abdelatif Chahboun",
"affiliation": None,
},
{
"slug": "mustapha-el-merroun",
"full_name_ar": "مصطفى المرون",
"full_name_lat": "Mustapha El Merroun",
"affiliation": None,
},
]

DOCUMENTS = [
{
"file_key": "library/usul-harb-al-rif.pdf",
"title": "أصول حرب الريف",
"abstract": "دراسة تاريخية حول أصول حرب الريف وسياقاتها السياسية والعسكرية، من تأليف المؤرخ جرمان عياش.",
"type": DocumentType.book,
"lang": "ar",
"year": 1992,
"pages": 375,
"doi": None,
"isbn": None,
"issn": None,
"primary_category_slug": "library",
"journal_slug": None,
"issue_key": None,
"start_page": None,
"end_page": None,
"cover_image_url": None,
"author_slugs": ["germain-ayache"],
},
{
"file_key": "library/dakirat-muarrikh.pdf",
"title": "ذاكرة مؤرخ",
"abstract": None,
"type": DocumentType.book,
"lang": "ar",
"year": None,
"pages": None,
"doi": None,
"isbn": None,
"issn": None,
"primary_category_slug": "library",
"journal_slug": None,
"issue_key": None,
"start_page": None,
"end_page": None,
"cover_image_url": None,
"author_slugs": [
"khalid-slaiki",
"oussama-ezzekari",
"zoubida-ben-ali-ouriaghli",
"mustapha-el-ghachi",
"abdelatif-chahboun",
"mustapha-el-merroun",
],
},
{
"file_key": "library/malamih-tarikh-tanja-1792-1947.pdf",
"title": "ملامح من تاريخ طنجة المعاصر، 1792-1947",
"abstract": "دراسة في بعض ملامح التاريخ المعاصر لمدينة طنجة خلال الفترة الممتدة من 1792 إلى 1947.",
"type": DocumentType.book,
"lang": "ar",
"year": 1996,
"pages": None,
"doi": None,
"isbn": None,
"issn": None,
"primary_category_slug": "library",
"journal_slug": None,
"issue_key": None,
"start_page": None,
"end_page": None,
"cover_image_url": None,
"author_slugs": ["abdelaziz-khallouk-temsamani"],
},
{
"file_key": "library/tanja-fi-tarikh-al-muasir-1800-1956.pdf",
"title": "طنجة في التاريخ المعاصر (1800-1956)",
"abstract": (
"مجموعة أبحاث حول تاريخ طنجة المعاصر، تتناول جوانب سياسية واجتماعية وثقافية "
"ودبلوماسية من تاريخ المدينة بين 1800 و1956."
),
"type": DocumentType.book,
"lang": "ar",
"year": 1991,
"pages": 541,
"doi": None,
"isbn": None,
"issn": None,
"primary_category_slug": "library",
"journal_slug": None,
"issue_key": None,
"start_page": None,
"end_page": None,
"cover_image_url": None,
"author_slugs": [],
},
]

CATEGORY_TRANSLATIONS = {
"library": {
"fr": {"title": "Bibliothèque", "description": None},
"es": {"title": "Biblioteca", "description": None},
"ar": {"title": "المكتبة", "description": None},
},
"journals": {
"fr": {"title": "Revues", "description": None},
"es": {"title": "Revistas", "description": None},
"ar": {"title": "المجلات", "description": None},
},
"archives": {
"fr": {"title": "Archives et patrimoine documentaire", "description": None},
"es": {"title": "Archivos y patrimonio documental", "description": None},
"ar": {"title": "الأرشيف والتراث الوثائقي", "description": None},
},
"historical-sites": {
"fr": {"title": "Sites et monuments historiques", "description": None},
"es": {"title": "Sitios y monumentos históricos", "description": None},
"ar": {"title": "المواقع والمعالم التاريخية", "description": None},
},
"research-themes": {
"fr": {"title": "Questions et problématiques de recherche", "description": None},
"es": {"title": "Cuestiones y problemáticas de investigación", "description": None},
"ar": {"title": "قضايا وإشكاليات البحث", "description": None},
},
"publications": {
"fr": {"title": "Publications", "description": None},
"es": {"title": "Publicaciones", "description": None},
"ar": {"title": "إصدارات", "description": None},
},
"manuscript": {
"fr": {"title": "Guide des collections de manuscrits", "description": None},
"es": {"title": "Guía de colecciones de manuscritos", "description": None},
"ar": {"title": "دليل مجموعات المخطوطات", "description": None},
},
"dar-al-niaba": {
    "fr": {"title": "Dar al-Niaba", "description": None},
    "es": {"title": "Dar al-Niaba", "description": None},
    "ar": {"title": "دار النيابة", "description": None},
},
"les-tangerois": {
    "fr": {"title": "Les Tangérois", "description": None},
    "es": {"title": "Los Tangerinos", "description": None},
    "ar": {"title": "الطنجيون", "description": None},
},

}

JOURNAL_TRANSLATIONS = {
"dar-al-niaba": {
"fr": {"title": "Dar al-Niaba", "description": None, "publisher": None},
"es": {"title": "Dar al-Niaba", "description": None, "publisher": None},
"ar": {"title": "دار النيابة", "description": None, "publisher": None},
},
"les-tangerois": {
"fr": {"title": "Les Tangérois", "description": None, "publisher": None},
"es": {"title": "Los Tangerinos", "description": None, "publisher": None},
"ar": {"title": "الطنجيون", "description": None, "publisher": None},
},
}


# ============================================================
# Helpers
# ============================================================


def _set_if_exists(obj: object, attr: str, value: object) -> None:
    if hasattr(obj, attr):
        setattr(obj, attr, value)


def get_category_by_slug(
    session,
    slug: str,
    *,
    kind: CategoryKind | None = None,
) -> Category | None:
    stmt = select(Category).where(Category.slug == slug)
    if kind is not None:
        stmt = stmt.where(Category.kind == kind)
    return session.execute(stmt.order_by(Category.id.asc())).scalars().first()


def get_journal_by_slug(session, slug: str) -> Journal | None:
    return session.execute(
        select(Journal)
        .where(Journal.slug == slug)
        .where(Journal.deleted_at.is_(None))
        .order_by(Journal.id.asc())
    ).scalars().first()


def get_author_by_slug(session, slug: str) -> Author | None:
    return session.execute(
        select(Author)
        .where(Author.slug == slug)
        .order_by(Author.id.asc())
    ).scalars().first()


def ensure_category(
    session,
    *,
    slug: str,
    name: str,
    kind: CategoryKind,
    description: str | None,
    parent: Category | None,
    order_index: int = 0,
    journal: Journal | None = None,
) -> Category:
    category = get_category_by_slug(session, slug, kind=kind)

    if category is None:
        category = Category(
            slug=slug,
            name=name,
            kind=kind,
            description=description,
            parent=parent,
            order_index=order_index,
            journal=journal if kind == CategoryKind.journal else None,
        )
        session.add(category)
        session.flush()
        return category

    category.name = name
    category.description = description
    category.parent = parent
    category.order_index = order_index
    category.journal = journal if kind == CategoryKind.journal else None
    session.flush()
    return category


def ensure_journal(
    session,
    *,
    slug: str,
    name: str,
    issn: str | None,
    publisher: str | None,
    description: str | None,
    cover_image_url: str | None,
) -> Journal:
    journal = get_journal_by_slug(session, slug)

    if journal is None:
        journal = Journal(
            slug=slug,
            name=name,
            issn=issn,
            publisher=publisher,
            description=description,
            cover_image_url=cover_image_url,
        )
        session.add(journal)
        session.flush()
        return journal

    journal.name = name
    journal.issn = issn
    journal.publisher = publisher
    journal.description = description
    journal.cover_image_url = cover_image_url
    _set_if_exists(journal, 'deleted_at', None)
    session.flush()
    return journal


def ensure_author(
    session,
    *,
    slug: str,
    full_name_ar: str,
    full_name_lat: str | None,
    affiliation: str | None,
) -> Author:
    author = get_author_by_slug(session, slug)

    if author is None:
        author = session.execute(
            select(Author)
            .where(Author.full_name_ar == full_name_ar)
            .order_by(Author.id.asc())
        ).scalars().first()

    if author is None:
        author = Author(
            slug=slug,
            full_name_ar=full_name_ar,
            full_name_lat=full_name_lat,
            affiliation=affiliation,
        )
        session.add(author)
        session.flush()
        return author

    author.slug = slug
    author.full_name_ar = full_name_ar
    author.full_name_lat = full_name_lat
    author.affiliation = affiliation
    _set_if_exists(author, 'deleted_at', None)
    session.flush()
    return author


def set_document_authors(document: Document, authors: Sequence[Author]) -> None:
    existing = {link.author_id: link for link in document.author_links}
    desired_ids: set[int] = set()

    for position, author in enumerate(authors, start=1):
        desired_ids.add(author.id)
        link = existing.get(author.id)
        if link is None:
            link = DocumentAuthor(author_id=author.id, position=position)
            document.author_links.append(link)
        else:
            link.position = position

    for link in list(document.author_links):
        if link.author_id not in desired_ids:
            document.author_links.remove(link)


def ensure_document(session, payload: dict, author_by_slug: dict[str, Author]) -> Document:
    file_key = payload['file_key']
    document = session.execute(
        select(Document)
        .where(Document.file_key == file_key)
        .order_by(Document.id.asc())
    ).scalars().first()

    if document is None:
        document = Document(file_key=file_key, title=payload['title'], type=payload['type'], lang=payload['lang'])
        session.add(document)
        session.flush()

    document.title = payload['title']
    document.abstract = payload.get('abstract')
    document.type = payload['type']
    document.lang = payload['lang']
    document.year = payload.get('year')
    document.pages = payload.get('pages')
    document.doi = payload.get('doi')
    document.isbn = payload.get('isbn')
    document.issn = payload.get('issn')
    document.file_key = file_key

    primary_category_slug = payload.get('primary_category_slug')
    document.primary_category = (
        get_category_by_slug(session, primary_category_slug) if primary_category_slug else None
    )

    journal_slug = payload.get('journal_slug')
    document.journal = get_journal_by_slug(session, journal_slug) if journal_slug else None
    document.issue = None
    document.start_page = payload.get('start_page')
    document.end_page = payload.get('end_page')
    document.cover_image_url = payload.get('cover_image_url')
    _set_if_exists(document, 'deleted_at', None)

    authors = [
        author_by_slug[slug]
        for slug in payload.get('author_slugs', [])
        if slug in author_by_slug
    ]
    set_document_authors(document, authors)

    session.flush()
    return document


def _category_translations_table() -> sa.Table:
    return sa.Table(
        "category_translations",
        sa.MetaData(),
        sa.Column("id", sa.Integer),
        sa.Column("category_id", sa.Integer),
        sa.Column("locale", sa.Text),
        sa.Column("title", sa.Text),
        sa.Column("description", sa.Text),
    )


def _journal_translations_table() -> sa.Table:
    return sa.Table(
        "journal_translations",
        sa.MetaData(),
        sa.Column("id", sa.Integer),
        sa.Column("journal_id", sa.Integer),
        sa.Column("locale", sa.String(10)),
        sa.Column("title", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("publisher", sa.Text),
    )


def upsert_category_translation(
    session,
    *,
    category_id: int,
    locale: str,
    title: str,
    description: str | None,
) -> None:
    table = _category_translations_table()
    existing_id = session.execute(
        select(table.c.id)
        .where(table.c.category_id == category_id)
        .where(table.c.locale == locale)
    ).scalar_one_or_none()

    values = {
        'category_id': category_id,
        'locale': locale,
        'title': title,
        'description': description,
    }
    if existing_id is None:
        session.execute(table.insert().values(**values))
    else:
        session.execute(table.update().where(table.c.id == existing_id).values(**values))


def upsert_journal_translation(
    session,
    *,
    journal_id: int,
    locale: str,
    title: str,
    description: str | None,
    publisher: str | None,
) -> None:
    table = _journal_translations_table()
    existing_id = session.execute(
        select(table.c.id)
        .where(table.c.journal_id == journal_id)
        .where(table.c.locale == locale)
    ).scalar_one_or_none()

    values = {
        'journal_id': journal_id,
        'locale': locale,
        'title': title,
        'description': description,
        'publisher': publisher,
    }
    if existing_id is None:
        session.execute(table.insert().values(**values))
    else:
        session.execute(table.update().where(table.c.id == existing_id).values(**values))


# ============================================================
# Main routine
# ============================================================


def run() -> None:
    session = SessionLocal()
    try:
        category_by_slug: dict[str, Category] = {}

        for item in SECTIONS:
            category = ensure_category(
                session,
                slug=item['slug'],
                name=item['name'],
                kind=item['kind'],
                description=item['description'],
                parent=None,
                order_index=item['order_index'],
                journal=None,
            )
            category_by_slug[item['slug']] = category

        for item in SUBCATEGORIES:
            parent = category_by_slug[item['parent_slug']]
            category = ensure_category(
                session,
                slug=item['slug'],
                name=item['name'],
                kind=item['kind'],
                description=item['description'],
                parent=parent,
                order_index=item['order_index'],
                journal=None,
            )
            category_by_slug[item['slug']] = category

        journal_by_slug: dict[str, Journal] = {}
        journals_parent = category_by_slug['journals']

        for item in JOURNALS:
            journal = ensure_journal(
                session,
                slug=item['slug'],
                name=item['name'],
                issn=item['issn'],
                publisher=item['publisher'],
                description=item['description'],
                cover_image_url=item['cover_image_url'],
            )
            journal_by_slug[item['slug']] = journal

            category = ensure_category(
                session,
                slug=item['slug'],
                name=item['name'],
                kind=CategoryKind.journal,
                description=item['category_description'],
                parent=journals_parent,
                order_index=item['order_index'],
                journal=journal,
            )
            category_by_slug[item['slug']] = category

        author_by_slug: dict[str, Author] = {}
        for item in AUTHORS:
            author = ensure_author(
                session,
                slug=item['slug'],
                full_name_ar=item['full_name_ar'],
                full_name_lat=item['full_name_lat'],
                affiliation=item['affiliation'],
            )
            author_by_slug[item['slug']] = author

        for item in DOCUMENTS:
            ensure_document(session, item, author_by_slug)

        for category_slug, locales in CATEGORY_TRANSLATIONS.items():
            category = category_by_slug.get(category_slug) or get_category_by_slug(session, category_slug)
            if category is None:
                continue

            for locale, payload in locales.items():
                title = payload.get('title')
                if not title:
                    continue
                upsert_category_translation(
                    session,
                    category_id=category.id,
                    locale=locale,
                    title=title,
                    description=payload.get('description'),
                )

        for journal_slug, locales in JOURNAL_TRANSLATIONS.items():
            journal = journal_by_slug.get(journal_slug) or get_journal_by_slug(session, journal_slug)
            if journal is None:
                continue

            for locale, payload in locales.items():
                title = payload.get('title')
                if not title:
                    continue
                upsert_journal_translation(
                    session,
                    journal_id=journal.id,
                    locale=locale,
                    title=title,
                    description=payload.get('description'),
                    publisher=payload.get('publisher'),
                )

        session.commit()
        print('Production seed completed successfully.')
        print(f'Sections/subcategories/journal categories: {len(category_by_slug)}')
        print(f'Journals: {len(journal_by_slug)}')
        print(f'Authors: {len(author_by_slug)}')
        print(f'Documents: {len(DOCUMENTS)}')
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    run()
