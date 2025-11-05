"""Seed historical site records for demo data.

Run order:
1) python -m scripts.dev_seed_categories
2) python -m scripts.dev_seed_journals
3) python -m scripts.dev_seed_archives
4) python -m scripts.dev_seed_sites
5) python -m scripts.dev_seed_research_themes
6) python -m scripts.dev_seed_publications

Quick verification:
curl "http://127.0.0.1:8010/v1/categories?parent=archives"
curl "http://127.0.0.1:8010/v1/search/documents?category_slug=historical-sites"
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


SITE_AUTHOR_PROFILES: tuple[tuple[str, str | None, str | None], ...] = (
    ("نادية بوعمرو", "Nadia Bouamrou", "برنامج توثيق المعالم التاريخية"),
    ("سعيد المجدوبي", "Said El Majdoub", "مختبر ترميم المواقع"),
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
    "historical-sites": (
        "Historical Sites",
        CategoryKind.section,
        "Documentation of architectural ensembles, archaeological sites, and cultural landscapes.",
        None,
    )
}


SITE_SEEDS: tuple[DocumentSeed, ...] = (
    DocumentSeed(
        title="Geospatial Survey of the Chellah Necropolis (2021)",
        abstract=(
            "This survey digitises the funerary terraces of Chellah using LiDAR and archival overlays. "
            "It documents water management features that connect the Merinid zawiya to Roman-era infrastructure. "
            "Recommendations address visitor circulation and habitat protection for the resident storks."
        ),
        lang="en",
        year=2021,
        doc_type=DocumentType.site_record,
        primary_category_slug="historical-sites",
        pages=58,
    ),
    DocumentSeed(
        title="Rapport photogrammétrique sur la kasbah d'Agadir Oufella",
        abstract=(
            "Ce rapport assemble une couverture photogrammétrique haute résolution de la kasbah d'Agadir Oufella. "
            "Il compare les élévations actuelles aux relevés militaires de 1934 pour mesurer l'impact du séisme de 1960. "
            "Des annexes décrivent les protocoles de consolidation et les consultations communautaires menées en 2019."
        ),
        lang="fr",
        year=2019,
        doc_type=DocumentType.site_record,
        primary_category_slug="historical-sites",
        pages=74,
    ),
    DocumentSeed(
        title="ملف حفظ موقع وليلي الأثري",
        abstract=(
            "يستعرض هذا الملف خطة شاملة لصيانة بقايا مدينة وليلي الرومانية. "
            "يتضمن تحليلاً لتدهور الأعمدة، ومسحاً للفسيفساء، وبرنامجاً لتدريب الحرفيين المحليين. "
            "كما يقدم توصيات لإشراك المجتمعات القروية المحيطة في جهود الحماية."
        ),
        lang="ar",
        year=2014,
        doc_type=DocumentType.site_record,
        primary_category_slug="historical-sites",
        pages=96,
    ),
    DocumentSeed(
        title="Structural Assessment of the Portuguese Cistern in El Jadida",
        abstract=(
            "Engineers and conservation architects collaborated on this assessment of the vaulted cistern beneath the Portuguese fortress. "
            "Moisture monitoring and salt crystallisation patterns were studied across two annual cycles. "
            "The report proposes phased interventions that safeguard nightly cultural programming."
        ),
        lang="en",
        year=2018,
        doc_type=DocumentType.site_record,
        primary_category_slug="historical-sites",
    ),
    DocumentSeed(
        title="Étude de restauration des remparts de Taza",
        abstract=(
            "Cette étude détaille la morphologie des remparts mérinides et saadien qui enveloppent la ville de Taza. "
            "Elle s'appuie sur des sources cartographiques ottomanes et sur des levés laser réalisés en 1996. "
            "Un plan de chantier progressif est proposé pour réhabiliter les portes monumentales."
        ),
        lang="fr",
        year=1997,
        doc_type=DocumentType.site_record,
        primary_category_slug="historical-sites",
        pages=88,
    ),
    DocumentSeed(
        title="Inventory of Oasis Watchtowers in Tafilalt",
        abstract=(
            "The inventory catalogues 47 agadir and watchtower structures scattered across the Tafilalt oasis network. "
            "It records oral histories on seasonal migration and defensive signalling. "
            "Comparative sketches situate each tower within a century-long chronology of flood responses."
        ),
        lang="en",
        year=2007,
        doc_type=DocumentType.site_record,
        primary_category_slug="historical-sites",
        pages=102,
    ),
    DocumentSeed(
        title="مذكرات صيانة مسار المواكب بزاوية تمكروت",
        abstract=(
            "يتابع هذا التقرير مراحل صيانة مسار المواكب الدينية بزاوية تمكروت في وادي درعة. "
            "يعتمد على مقابلات مع الطلبة والحرفيين الذين يشرفون على تجهيز الساحات والأروقة التاريخية. "
            "تتضمن الخاتمة جدولاً زمنياً لتنفيذ الأشغال قبل موسم العيد الكبير."
        ),
        lang="ar",
        year=2022,
        doc_type=DocumentType.site_record,
        primary_category_slug="historical-sites",
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
        for profile in SITE_AUTHOR_PROFILES
    ]
    set_document_authors(document, authors)
    return created, updated


def seed() -> None:
    session = SessionLocal()
    inserted = 0
    updated = 0
    try:
        categories = ensure_required_categories(session)
        for seed_row in SITE_SEEDS:
            created, changed = upsert_document(session, seed_row, categories)
            inserted += int(created)
            updated += int(changed and not created)

        session.commit()
        print(
            f"Historical site records seeded — inserted: {inserted}, updated: {updated}, total: {len(SITE_SEEDS)}."
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
