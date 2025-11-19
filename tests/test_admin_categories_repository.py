from __future__ import annotations

from sqlalchemy import event

from app.models.category import Category, CategoryKind
from app.repositories.admin_categories import CategoryAdminRepository


def _insert_category(session, *, name: str, slug: str, kind: CategoryKind, parent_id: int | None = None, order: int = 0) -> Category:
    category = Category(
        name=name,
        slug=slug,
        kind=kind,
        parent_id=parent_id,
        order_index=order,
    )
    session.add(category)
    session.flush()
    return category


def test_tree_query_count_is_bounded(head_database) -> None:
    SessionLocal, engine = head_database
    with SessionLocal.begin() as session:
        parent = _insert_category(session, name="Root", slug="root", kind=CategoryKind.topic)
        for index in range(50):
            _insert_category(
                session,
                name=f"Child {index}",
                slug=f"child-{index}",
                kind=CategoryKind.topic,
                parent_id=parent.id,
                order=index,
            )

    counter = {"count": 0}

    def _count_queries(_conn, _cursor, _statement, _params, _context, _executemany):
        counter["count"] += 1

    event.listen(engine, "before_cursor_execute", _count_queries)
    try:
        with SessionLocal() as session:
            repo = CategoryAdminRepository(session)
            nodes = repo.get_tree(kind=CategoryKind.topic, max_depth=2, include_counts=True)
            assert nodes and len(nodes[0].children or []) == 50
    finally:
        event.remove(engine, "before_cursor_execute", _count_queries)

    assert counter["count"] <= 4


def test_children_query_count_is_bounded(head_database) -> None:
    SessionLocal, engine = head_database
    with SessionLocal.begin() as session:
        parent = _insert_category(session, name="Root", slug="root", kind=CategoryKind.topic)
        for index in range(40):
            _insert_category(
                session,
                name=f"Child {index}",
                slug=f"child-{index}",
                kind=CategoryKind.topic,
                parent_id=parent.id,
                order=index,
            )
        parent_id = parent.id

    counter = {"count": 0}

    def _count_queries(_conn, _cursor, _statement, _params, _context, _executemany):
        counter["count"] += 1

    event.listen(engine, "before_cursor_execute", _count_queries)
    try:
        with SessionLocal() as session:
            repo = CategoryAdminRepository(session)
            nodes = repo.get_children(parent_id=parent_id, kind=CategoryKind.topic, include_counts=True)
            assert len(nodes) == 40
    finally:
        event.remove(engine, "before_cursor_execute", _count_queries)

    assert counter["count"] <= 3
