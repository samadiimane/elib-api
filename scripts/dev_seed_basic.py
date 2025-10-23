"""Development helper to seed baseline taxonomy and sample documents."""
# scripts/dev_seed_basic.py

from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Category, CategoryKind, Document, DocumentType, Journal, JournalIssue
from sqlalchemy.orm import configure_mappers
configure_mappers()



def get_or_create_category(
    session,
    *,
    slug: str,
    name: str,
    kind: CategoryKind,
    parent: Category | None = None,
) -> Category:
    stmt = select(Category).where(Category.slug == slug)
    instance = session.execute(stmt).scalar_one_or_none()
    if instance:
        return instance

    category = Category(slug=slug, name=name, kind=kind, parent=parent)
    session.add(category)
    session.flush()
    return category


def get_or_create_document(session, *, title: str, defaults: dict) -> Document:
    stmt = select(Document).where(Document.title == title)
    instance = session.execute(stmt).scalar_one_or_none()
    if instance:
        return instance

    document = Document(title=title, **defaults)
    session.add(document)
    session.flush()
    return document


def main() -> None:
    session = SessionLocal()
    try:
        # Root sections
        library = get_or_create_category(
            session,
            slug="library",
            name="Library",
            kind=CategoryKind.section,
        )
        journals = get_or_create_category(
            session,
            slug="journals",
            name="Journals",
            kind=CategoryKind.section,
        )
        archives = get_or_create_category(
            session,
            slug="archives",
            name="Archives & Documentary Heritage",
            kind=CategoryKind.section,
        )
        sites = get_or_create_category(
            session,
            slug="sites",
            name="Historical Sites & Landmarks",
            kind=CategoryKind.section,
        )
        issues = get_or_create_category(
            session,
            slug="issues",
            name="Research Issues & Problematics",
            kind=CategoryKind.section,
        )

        # Sample journal under journals
        dar = get_or_create_category(
            session,
            slug="dar",
            name="Dar Al-Niaba",
            kind=CategoryKind.journal,
            parent=journals,
        )

        # Sample documents
        samples = [
            (
                "An Introduction to Moroccan Trade Routes",
                {
                    "abstract": "Survey of trans-Saharan commerce between the 16th and 19th centuries.",
                    "type": DocumentType.article,
                    "lang": "en",
                    "year": 2020,
                    "pages": 34,
                    "primary_category": dar,
                },
            ),
            (
                "Catalogue of Rif Manuscripts",
                {
                    "abstract": "Annotated catalogue of manuscripts preserved in the Rif region.",
                    "type": DocumentType.archive_item,
                    "lang": "fr",
                    "year": 1998,
                    "pages": 220,
                    "primary_category": archives,
                },
            ),
            (
                "Field Survey of Tangier Landmarks",
                {
                    "abstract": "Documentation of architectural heritage across Tangier.",
                    "type": DocumentType.report,
                    "lang": "ar",
                    "year": 2015,
                    "pages": 88,
                    "primary_category": sites,
                },
            ),
        ]

        for title, defaults in samples:
            get_or_create_document(session, title=title, defaults=defaults)

        session.commit()
        print("Seed completed (basic categories & documents).")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
