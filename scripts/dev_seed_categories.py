"""Development helper script to seed baseline navigation categories."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.category import Category, CategoryKind

SeedNode = dict[str, object]


SEED_TREE: tuple[SeedNode, ...] = (
    {"slug": "library", "name": "Library", "kind": CategoryKind.section},
    {
        "slug": "journals",
        "name": "Journals",
        "kind": CategoryKind.section,
        "children": (
            {"slug": "dar", "name": "Dar Al-Niaba", "kind": CategoryKind.journal},
            {"slug": "tang", "name": "Les Tangérois", "kind": CategoryKind.journal},
        ),
    },
    {
        "slug": "archives",
        "name": "Archives & Documentary Heritage",
        "kind": CategoryKind.section,
        "children": (
            {
                "slug": "rif",
                "name": "Rif Sufi Manuscripts",
                "kind": CategoryKind.archive_collection,
            },
        ),
    },
    {"slug": "sites", "name": "Historical Sites & Landmarks", "kind": CategoryKind.section},
    {
        "slug": "issues",
        "name": "Research Issues & Problematics",
        "kind": CategoryKind.section,
        "children": (
            {
                "slug": "medieval",
                "name": "Medieval Moroccan Studies",
                "kind": CategoryKind.topic,
            },
        ),
    },
)


def ensure_category(session, slug: str, name: str, kind: CategoryKind, parent: Category | None = None) -> Category:
    stmt = select(Category).where(Category.slug == slug)
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        return existing

    category = Category(
        slug=slug,
        name=name,
        kind=kind,
        parent=parent,
    )
    session.add(category)
    session.flush()
    return category


def seed_children(session, parent: Category, children: Iterable[SeedNode]) -> None:
    for child in children:
        node = ensure_category(
            session,
            slug=str(child["slug"]),
            name=str(child["name"]),
            kind=child["kind"],
            parent=parent,
        )
        grandchildren = child.get("children")
        if grandchildren:
            seed_children(session, node, grandchildren)  # type: ignore[arg-type]


def seed() -> None:
    session = SessionLocal()
    try:
        for node in SEED_TREE:
            parent = ensure_category(
                session,
                slug=str(node["slug"]),
                name=str(node["name"]),
                kind=node["kind"],
            )
            children = node.get("children")
            if children:
                seed_children(session, parent, children)  # type: ignore[arg-type]

        session.commit()
        print("Seeded navigation categories.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
