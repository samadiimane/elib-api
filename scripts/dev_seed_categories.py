"""Seed a baseline navigation taxonomy with descriptive academic language."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Category, CategoryKind
from sqlalchemy.orm import configure_mappers

configure_mappers()


@dataclass(frozen=True)
class CategorySeed:
    slug: str
    name: str
    kind: CategoryKind
    description: str | None = None
    children: tuple["CategorySeed", ...] = field(default_factory=tuple)


SEED_TREE: tuple[CategorySeed, ...] = (
    CategorySeed(
        slug="library",
        name="Library",
        kind=CategoryKind.section,
        description="Gateway to monographs, edited volumes, research reports, and curated bibliographies.",
    ),
    CategorySeed(
        slug="journals",
        name="Journals",
        kind=CategoryKind.section,
        description="Serial publications that disseminate peer-reviewed scholarship across Maghribi studies.",
    ),
    CategorySeed(
        slug="archives",
        name="Archives & Documentary Heritage",
        kind=CategoryKind.section,
        description="Finding aids and digitized corpora derived from manuscript, epistolary, and administrative fonds.",
        children=(
            CategorySeed(
                slug="manuscript-guides",
                name="Guides to Manuscript Collections",
                kind=CategoryKind.archive_collection,
                description="Inventories and paleographic studies of Arabic, Amazigh, and Ottoman manuscripts.",
            ),
            CategorySeed(
                slug="digitization-projects",
                name="Digitization Initiatives",
                kind=CategoryKind.topic,
                description="Reports on preservation and digitization of fragile archival holdings.",
            ),
        ),
    ),
    CategorySeed(
        slug="heritage-sites",
        name="Heritage Sites & Landmarks",
        kind=CategoryKind.section,
        description="Documentation of architectural ensembles, archaeological sites, and landscape heritage.",
        children=(
            CategorySeed(
                slug="coastal-forts",
                name="Coastal Fortifications",
                kind=CategoryKind.topic,
                description="Studies of maritime defensive works spanning Portuguese, Spanish, and Moroccan polities.",
            ),
            CategorySeed(
                slug="sacred-architecture",
                name="Sacred Architecture",
                kind=CategoryKind.topic,
                description="Mosques, zawiyas, and pilgrimage complexes analysed through art historical lenses.",
            ),
        ),
    ),
    CategorySeed(
        slug="research-themes",
        name="Research Themes",
        kind=CategoryKind.section,
        description="Cross-cutting scholarly conversations connecting sources, spaces, and disciplines.",
        children=(
            CategorySeed(
                slug="urban-histories",
                name="Urban Histories",
                kind=CategoryKind.topic,
                description="Micro-histories of neighbourhoods, municipal governance, and everyday urban life.",
            ),
            CategorySeed(
                slug="intellectual-networks",
                name="Intellectual Networks",
                kind=CategoryKind.topic,
                description="Transmission of knowledge across scholarly lineages, madrasas, and Sufi lodges.",
            ),
            CategorySeed(
                slug="material-culture",
                name="Material Culture Studies",
                kind=CategoryKind.topic,
                description="Objects, artisanship, and museological practices anchored in the Maghrib.",
            ),
        ),
    ),
)


def ensure_category(
    session,
    *,
    slug: str,
    name: str,
    kind: CategoryKind,
    description: str | None,
    parent: Category | None = None,
) -> Category:
    stmt = select(Category).where(Category.slug == slug)
    category = session.execute(stmt).scalar_one_or_none()
    if category:
        category.name = name
        category.kind = kind
        category.description = description
        if parent and category.parent_id != parent.id:
            category.parent = parent
        return category

    category = Category(
        slug=slug,
        name=name,
        kind=kind,
        description=description,
        parent=parent,
    )
    session.add(category)
    session.flush()
    return category


def seed_children(session, parent: Category, children: Sequence[CategorySeed]) -> None:
    for child in children:
        node = ensure_category(
            session,
            slug=child.slug,
            name=child.name,
            kind=child.kind,
            description=child.description,
            parent=parent,
        )
        if child.children:
            seed_children(session, node, child.children)


def seed() -> None:
    session = SessionLocal()
    try:
        for node in SEED_TREE:
            parent = ensure_category(
                session,
                slug=node.slug,
                name=node.name,
                kind=node.kind,
                description=node.description,
                parent=None,
            )
            if node.children:
                seed_children(session, parent, node.children)

        session.commit()
        print("Seeded navigation categories.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
