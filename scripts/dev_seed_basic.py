"""Seed foundational documents that complement the journal corpus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Author, Category, Document, DocumentAuthor, DocumentType
from sqlalchemy.orm import configure_mappers

configure_mappers()


@dataclass(frozen=True)
class DocumentSeed:
    title: str
    abstract: str
    type: DocumentType
    lang: str
    year: int
    pages: int | None
    category_slug: str | None
    doi: str | None = None
    isbn: str | None = None
    issn: str | None = None


BASIC_AUTHOR_PROFILES: tuple[tuple[str, str | None, str | None], ...] = (
    ("هند العلمي", "Hind Alami", "مؤسسة تمسماني للبحث والدراسات"),
    ("مروان الطنجي", "Marouane Ettangi", "مختبر الأرشفة الرقمية"),
)

_AUTHOR_CACHE: dict[tuple[str, str | None, str | None], Author] = {}


def get_or_create_author(
    session,
    full_name_ar: str,
    full_name_lat: str | None = None,
    affiliation: str | None = None,
) -> Author:
    key = (full_name_ar, full_name_lat, affiliation)
    cached = _AUTHOR_CACHE.get(key)
    if cached is not None:
        return cached

    stmt = select(Author).where(Author.full_name_ar == full_name_ar)
    if full_name_lat is not None:
        stmt = stmt.where(Author.full_name_lat == full_name_lat)
    author = session.execute(stmt).scalar_one_or_none()

    if author is None:
        author = Author(
            full_name_ar=full_name_ar,
            full_name_lat=full_name_lat,
            affiliation=affiliation,
        )
        session.add(author)
        session.flush()
    else:
        updated = False
        if full_name_lat is not None and author.full_name_lat != full_name_lat:
            author.full_name_lat = full_name_lat
            updated = True
        if affiliation is not None and author.affiliation != affiliation:
            author.affiliation = affiliation
            updated = True
        if updated:
            session.flush()

    _AUTHOR_CACHE[key] = author
    return author


def set_document_authors(document: Document, authors: Sequence[Author]) -> None:
    existing = {link.author_id: link for link in getattr(document, "author_links", [])}
    desired_ids: set[int] = set()

    for position, author in enumerate(authors, start=1):
        desired_ids.add(author.id)
        link = existing.get(author.id)
        if link is None:
            link = DocumentAuthor(author_id=author.id, position=position)
            document.author_links.append(link)
        else:
            link.position = position

    for link in list(getattr(document, "author_links", [])):
        if link.author_id not in desired_ids:
            document.author_links.remove(link)


DOCUMENT_SEEDS: tuple[DocumentSeed, ...] = (
    DocumentSeed(
        title="Atlas of Saharan Caravanserais",
        abstract="Synthesizes architectural surveys and caravan diaries to map Saharan waystations between Tindouf and Zagora.",
        type=DocumentType.report,
        lang="en",
        year=2018,
        pages=142,
        category_slug="heritage-sites",
        doi="10.3479/msr.2018.001",
    ),
    DocumentSeed(
        title="Catalogue of Idrisi Manuscripts at al-Qarawiyyin",
        abstract="Annotated catalogue describing codicological features of Idrisi lineage manuscripts preserved in Fes.",
        type=DocumentType.archive_item,
        lang="ar",
        year=2021,
        pages=312,
        category_slug="manuscript-guides",
        isbn="978-1-55555-482-3",
    ),
    DocumentSeed(
        title="Digitizing the Bilateral Protectorate Archives",
        abstract="Evaluates digitization workflows harmonizing Spanish and French archival metadata for shared holdings.",
        type=DocumentType.thesis,
        lang="fr",
        year=2019,
        pages=198,
        category_slug="digitization-projects",
    ),
    DocumentSeed(
        title="Crafting Brass Astrolabes in Seventeenth-Century Fes",
        abstract="Explores artisanal treatises and workshop inventories to contextualize scientific instruments within Maghribi craft guilds.",
        type=DocumentType.article,
        lang="en",
        year=2022,
        pages=27,
        category_slug="material-culture",
    ),
    DocumentSeed(
        title="Pilgrimage Networks of the Jbala Highlands",
        abstract="Oral narratives and ethnographic mapping illustrate seasonal pilgrimages linking shrine-based economies.",
        type=DocumentType.report,
        lang="ar",
        year=2017,
        pages=96,
        category_slug="sacred-architecture",
    ),
)


def get_category(session, slug: str | None) -> Category | None:
    if slug is None:
        return None
    stmt = select(Category).where(Category.slug == slug)
    return session.execute(stmt).scalar_one_or_none()


def upsert_document(session, seed: DocumentSeed) -> None:
    stmt = select(Document).where(Document.title == seed.title)
    document = session.execute(stmt.order_by(Document.id.asc())).scalars().first()
    category = get_category(session, seed.category_slug)

    if document:
        document.abstract = seed.abstract
        document.type = seed.type
        document.lang = seed.lang
        document.year = seed.year
        document.pages = seed.pages
        document.primary_category = category
        document.doi = seed.doi
        document.isbn = seed.isbn
        document.issn = seed.issn
    else:
        document = Document(
            title=seed.title,
            abstract=seed.abstract,
            type=seed.type,
            lang=seed.lang,
            year=seed.year,
            pages=seed.pages,
            primary_category=category,
            doi=seed.doi,
            isbn=seed.isbn,
            issn=seed.issn,
        )
        session.add(document)

    authors = [
        get_or_create_author(session, full_name_ar=profile[0], full_name_lat=profile[1], affiliation=profile[2])
        for profile in BASIC_AUTHOR_PROFILES
    ]
    set_document_authors(document, authors)


def run(seeds: Iterable[DocumentSeed] = DOCUMENT_SEEDS) -> None:
    session = SessionLocal()
    try:
        for seed in seeds:
            upsert_document(session, seed)
        session.commit()
        print("Seeded foundational standalone documents.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
