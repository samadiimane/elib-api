"""Seed foundation publications for demo data.

Run order:
1) python -m scripts.dev_seed_categories
2) python -m scripts.dev_seed_journals
3) python -m scripts.dev_seed_archives
4) python -m scripts.dev_seed_sites
5) python -m scripts.dev_seed_research_themes
6) python -m scripts.dev_seed_publications

Quick verification:
curl "http://127.0.0.1:8010/v1/search/documents?category_slug=publications"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

from app.db.session import SessionLocal
from app.models import (
    Author,
    Category,
    CategoryKind,
    Document,
    DocumentAuthor,
    DocumentType,
)

configure_mappers()


@dataclass(frozen=True)
class DocumentSeed:
    title: str
    abstract: str
    lang: str
    year: int
    doc_type: DocumentType
    primary_category_slug: str
    pages: int | None = None
    doi: str | None = None
    isbn: str | None = None
    issn: str | None = None


PUBLICATION_AUTHOR_PROFILES: tuple[tuple[str, str | None, str | None], ...] = (
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


CATEGORY_DEFAULTS = {
    "publications": (
        "Publications",
        CategoryKind.section,
        "Foundation publications, working papers, translations, and policy briefs released for public use.",
        None,
    )
}


PUBLICATION_SEEDS: tuple[DocumentSeed, ...] = (
    DocumentSeed(
        title="Atlas of Coastal Heritage Corridors",
        abstract=(
            "This richly illustrated volume maps maritime heritage corridors from Tangier to Dakhla. "
            "It integrates port registries, oral histories with fisherfolk, and remote-sensing imagery. "
            "Each chapter offers policy recommendations for climate adaptation and community stewardship."
        ),
        lang="en",
        year=2023,
        doc_type=DocumentType.book,
        primary_category_slug="publications",
        pages=248,
        isbn="978-1-90745-310-8",
    ),
    DocumentSeed(
        title="رسالة دكتوراه: سياسات الذاكرة في الرباط (1956-2011)",
        abstract=(
            "تتناول هذه الرسالة التحولات في سياسات الذاكرة بمدينة الرباط عبر خمسة عقود. "
            "تعتمد على أرشيفات بلدية، مقابلات مع ساكنة المدينة، وتحليل للخطاب البصري في الساحات العامة. "
            "تختتم بخارطة طريق للمصالحة بين الإرث الاستعماري والحكايات المحلية."
        ),
        lang="ar",
        year=2021,
        doc_type=DocumentType.thesis,
        primary_category_slug="publications",
        pages=362,
        isbn="978-9931-9123-75-6",
    ),
    DocumentSeed(
        title="Translating Archives: Oral Histories into Metadata",
        abstract=(
            "This article examines how community oral history projects can be described within interoperable metadata schemas. "
            "Case studies from Tetouan and Safi demonstrate blended workflows between cataloguers and narrators. "
            "The piece proposes Arabic-language controlled vocabularies for intangible heritage collections."
        ),
        lang="en",
        year=2022,
        doc_type=DocumentType.article,
        primary_category_slug="publications",
        pages=27,
        doi="10.48231/atlas.2022.metadata",
        issn="2617-1310",
    ),
    DocumentSeed(
        title="Programme de formation des archivistes communautaires",
        abstract=(
            "Ce rapport décrit un programme de formation destiné aux archivistes communautaires des oasis du Sud. "
            "Il détaille les modules pédagogiques, les outils open-source utilisés, et les retours d'évaluation des participantes. "
            "Une annexe présente des fiches techniques pour la préservation de supports fragiles."
        ),
        lang="fr",
        year=2020,
        doc_type=DocumentType.report,
        primary_category_slug="publications",
        pages=112,
    ),
    DocumentSeed(
        title="Manual for Community Digitisation Labs",
        abstract=(
            "This handbook guides facilitators who establish digitisation labs in rural libraries. "
            "It covers ethical capture workflows, power backup solutions, and multilingual descriptive standards. "
            "Checklists and troubleshooting charts are adapted from three pilot sites in the Middle Atlas."
        ),
        lang="en",
        year=2019,
        doc_type=DocumentType.book,
        primary_category_slug="publications",
        pages=164,
        isbn="978-1-63964-018-2",
    ),
    DocumentSeed(
        title="Comparative Study of Maghribi Bibliographic Standards",
        abstract=(
            "The study analyses bibliographic standards adopted by university libraries in Rabat, Tunis, and Algiers. "
            "It evaluates the treatment of Arabic-script authority files and transliteration practices. "
            "Recommendations advocate shared governance between cataloguing departments and digital scholarship labs."
        ),
        lang="en",
        year=2018,
        doc_type=DocumentType.report,
        primary_category_slug="publications",
        pages=89,
    ),
    DocumentSeed(
        title="مجلة المؤسسة: عدد خاص حول الأرشيف الشفهي",
        abstract=(
            "يقدم هذا العدد الخاص حوارات وشهادات صوتية حول الأرشيف الشفهي في المغرب الكبير. "
            "يتضمن مقالات معمقة عن طرق التدريب الميداني وأخلاقيات جمع الذاكرة الجماعية. "
            "كما يعرض تجارب رقمية تستخدم الخرائط التشاركية لتوثيق الرواية الشعبية."
        ),
        lang="ar",
        year=2024,
        doc_type=DocumentType.article,
        primary_category_slug="publications",
        pages=31,
        doi="10.48231/atlas.2024.oralhistory",
        issn="2790-4478",
    ),
)


def get_category_by_slug(session, slug: str) -> Category | None:
    return session.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()


def ensure_category(
    session,
    *,
    slug: str,
    name: str,
    kind: CategoryKind,
    description: str,
    parent: Category | None = None,
) -> tuple[Category, bool, bool]:
    category = get_category_by_slug(session, slug)
    if category is None:
        category = Category(
            slug=slug,
            name=name,
            kind=kind,
            description=description,
            parent=parent,
        )
        session.add(category)
        session.flush()
        return category, True, False

    updated = False
    if category.name != name:
        category.name = name
        updated = True
    if category.kind != kind:
        category.kind = kind
        updated = True
    if category.description != description:
        category.description = description
        updated = True
    if parent is None and category.parent_id is not None:
        category.parent = None
        updated = True
    if parent is not None and category.parent_id != parent.id:
        category.parent = parent
        updated = True
    return category, False, updated


def ensure_required_categories(session) -> dict[str, Category]:
    resolved: dict[str, Category] = {}
    for slug, (name, kind, description, parent_slug) in CATEGORY_DEFAULTS.items():
        parent = resolved.get(parent_slug) if parent_slug else None
        if parent_slug and parent is None:
            parent = get_category_by_slug(session, parent_slug)
            if parent is None:
                parent_name, parent_kind, parent_desc, _ = CATEGORY_DEFAULTS[parent_slug]
                parent, _, _ = ensure_category(
                    session,
                    slug=parent_slug,
                    name=parent_name,
                    kind=parent_kind,
                    description=parent_desc,
                    parent=None,
                )
            resolved[parent_slug] = parent
        category, _, _ = ensure_category(
            session,
            slug=slug,
            name=name,
            kind=kind,
            description=description,
            parent=parent,
        )
        resolved[slug] = category
    return resolved


def upsert_document(session, seed: DocumentSeed, categories: dict[str, Category]) -> tuple[bool, bool]:
    document = (
        session.execute(
            select(Document).where(Document.title == seed.title).order_by(Document.id.asc())
        )
        .scalars()
        .first()
    )
    created = False
    updated = False
    category = categories[seed.primary_category_slug]

    def maybe_set(obj: Document, attr: str, value):
        nonlocal updated
        if getattr(obj, attr) != value:
            setattr(obj, attr, value)
            updated = True

    if document is None:
        document = Document(
            title=seed.title,
            abstract=seed.abstract,
            lang=seed.lang,
            year=seed.year,
            type=seed.doc_type,
            pages=seed.pages,
            doi=seed.doi,
            isbn=seed.isbn,
            issn=seed.issn,
            primary_category=category,
        )
        session.add(document)
        session.flush()
        created = True
    else:
        maybe_set(document, "abstract", seed.abstract)
        maybe_set(document, "lang", seed.lang)
        maybe_set(document, "year", seed.year)
        if document.type != seed.doc_type:
            document.type = seed.doc_type
            updated = True
        maybe_set(document, "pages", seed.pages)
        maybe_set(document, "doi", seed.doi)
        maybe_set(document, "isbn", seed.isbn)
        maybe_set(document, "issn", seed.issn)
        if document.primary_category_id != category.id:
            document.primary_category = category
            updated = True

    authors = [
        get_or_create_author(session, full_name_ar=profile[0], full_name_lat=profile[1], affiliation=profile[2])
        for profile in PUBLICATION_AUTHOR_PROFILES
    ]
    set_document_authors(document, authors)
    return created, updated


def seed() -> None:
    session = SessionLocal()
    inserted = 0
    updated = 0
    try:
        categories = ensure_required_categories(session)
        for seed_row in PUBLICATION_SEEDS:
            created, changed = upsert_document(session, seed_row, categories)
            inserted += int(created)
            updated += int(changed and not created)

        session.commit()
        print(
            f"Publications seeded — inserted: {inserted}, updated: {updated}, total: {len(PUBLICATION_SEEDS)}."
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
