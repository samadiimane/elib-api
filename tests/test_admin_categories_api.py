from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import auth as auth_dependencies
from app.api.routes import admin_categories as admin_categories_routes
from app.main import app
from app.models.category import Category, CategoryKind
from app.models.journal import Journal
from app.models.document import Document, DocumentType
from app.models.user import UserRoleEnum


def _override_db(SessionLocal):
    def dependency():
        with SessionLocal() as session:
            yield session

    return dependency


def _admin_identity():
    return SimpleNamespace(
        id=0,
        email="admin@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=UserRoleEnum.admin)],
    )


def _apply_admin_overrides(SessionLocal):
    app.dependency_overrides[admin_categories_routes.get_db] = _override_db(SessionLocal)
    app.dependency_overrides[auth_dependencies.get_current_user] = lambda: _admin_identity()


def _clear_overrides():
    app.dependency_overrides.pop(admin_categories_routes.get_db, None)
    app.dependency_overrides.pop(auth_dependencies.get_current_user, None)


def _insert_category(session, *, name: str, slug: str, kind: CategoryKind, parent: Category | None = None, journal_id: int | None = None) -> Category:
    category = Category(
        name=name,
        slug=slug,
        kind=kind,
        parent_id=parent.id if parent else None,
        journal_id=journal_id,
    )
    session.add(category)
    session.flush()
    return category


def test_children_response_includes_kind_slug_and_journal_id(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        parent = _insert_category(session, name="Parent", slug="parent-for-children", kind=CategoryKind.section)
        journal = Journal(slug="linked-journal", name="Linked Journal")
        session.add(journal)
        session.flush()
        journal_id = journal.id
        _insert_category(
            session,
            name="Journal Child",
            slug="journal-child",
            kind=CategoryKind.journal,
            parent=parent,
            journal_id=journal_id,
        )
        _insert_category(
            session,
            name="Topic Child",
            slug="topic-child",
            kind=CategoryKind.topic,
            parent=parent,
        )
        parent_id = parent.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        response = client.get(f"/v1/admin/categories/children/{parent_id}")
        assert response.status_code == 200, response.text
        items = response.json()
        assert isinstance(items, list)
        by_slug = {item["slug"]: item for item in items}
        assert set(by_slug) == {"journal-child", "topic-child"}

        journal_child = by_slug["journal-child"]
        assert journal_child["kind"] == CategoryKind.journal.value
        assert "journal_id" in journal_child
        assert journal_child["journal_id"] == journal_id

        topic_child = by_slug["topic-child"]
        assert topic_child["kind"] == CategoryKind.topic.value
        assert "journal_id" in topic_child
        assert topic_child["journal_id"] is None
    finally:
        _clear_overrides()


def test_create_category_duplicate_slug_conflict(head_database) -> None:
    SessionLocal, _engine = head_database
    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        payload = {
            "name": "Root Topic",
            "slug": "root-topic",
            "kind": "topic",
            "parent_id": None,
        }
        first = client.post("/v1/admin/categories", json=payload)
        assert first.status_code == 201, first.text

        duplicate = client.post("/v1/admin/categories", json=payload)
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"]["user_message"]
    finally:
        _clear_overrides()


def test_reorder_siblings_applies_new_order(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        parent = _insert_category(session, name="Parent", slug="parent", kind=CategoryKind.topic)
        first = _insert_category(session, name="First", slug="first", kind=CategoryKind.topic, parent=parent)
        second = _insert_category(session, name="Second", slug="second", kind=CategoryKind.topic, parent=parent)
        third = _insert_category(session, name="Third", slug="third", kind=CategoryKind.topic, parent=parent)
        parent_id = parent.id
        first_id = first.id
        second_id = second.id
        third_id = third.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        payload = {
            "parent_id": parent_id,
            "items": [
                {"id": second_id, "order": 0},
                {"id": third_id, "order": 1},
                {"id": first_id, "order": 2},
            ],
        }
        response = client.patch("/v1/admin/categories/reorder", json=payload)
        assert response.status_code == 200, response.text
        with SessionLocal() as session:
            ordered = session.execute(
                select(Category).where(Category.id.in_([first_id, second_id, third_id])).order_by(Category.order_index.asc())
            ).scalars().all()
            assert [category.slug for category in ordered] == ["second", "third", "first"]
    finally:
        _clear_overrides()


def test_move_category_between_parents(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        parent_a = _insert_category(session, name="Parent A", slug="parent-a", kind=CategoryKind.topic)
        parent_b = _insert_category(session, name="Parent B", slug="parent-b", kind=CategoryKind.topic)
        child = _insert_category(session, name="Child", slug="child", kind=CategoryKind.topic, parent=parent_a)
        parent_b_id = parent_b.id
        child_id = child.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        response = client.patch(f"/v1/admin/categories/{child_id}/move", json={"parent_id": parent_b_id, "order": 0})
        assert response.status_code == 200, response.text
        with SessionLocal() as session:
            moved = session.get(Category, child_id)
            assert moved.parent_id == parent_b_id
            assert moved.order_index == 0
    finally:
        _clear_overrides()


def test_move_category_cycle_conflict(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        root = _insert_category(session, name="Root", slug="root", kind=CategoryKind.topic)
        child = _insert_category(session, name="Child", slug="child", kind=CategoryKind.topic, parent=root)
        grandchild = _insert_category(session, name="Grandchild", slug="grandchild", kind=CategoryKind.topic, parent=child)
        root_id = root.id
        grandchild_id = grandchild.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        response = client.patch(f"/v1/admin/categories/{root_id}/move", json={"parent_id": grandchild_id})
        assert response.status_code == 409
        assert "descendants" in response.json()["detail"]["user_message"]
    finally:
        _clear_overrides()


def test_move_category_to_root(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        parent = _insert_category(session, name="Parent", slug="parent-move", kind=CategoryKind.topic)
        child = _insert_category(session, name="Child", slug="child-move", kind=CategoryKind.topic, parent=parent)
        child_id = child.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        response = client.patch(f"/v1/admin/categories/{child_id}/move", json={"parent_id": None})
        assert response.status_code == 200
        with SessionLocal() as session:
            moved = session.get(Category, child_id)
            assert moved.parent_id is None
    finally:
        _clear_overrides()


def test_move_category_updates_order_within_parent(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        parent = _insert_category(session, name="Parent", slug="parent-order", kind=CategoryKind.topic)
        first = _insert_category(session, name="First", slug="first-order", kind=CategoryKind.topic, parent=parent)
        second = _insert_category(session, name="Second", slug="second-order", kind=CategoryKind.topic, parent=parent)
        third = _insert_category(session, name="Third", slug="third-order", kind=CategoryKind.topic, parent=parent)
        second_id = second.id
        parent_id = parent.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        response = client.patch(f"/v1/admin/categories/{second_id}/move", json={"parent_id": parent_id, "order": 2})
        assert response.status_code == 200
        with SessionLocal() as session:
            ordered = session.execute(
                select(Category).where(Category.parent_id == parent_id).order_by(Category.order_index.asc())
            ).scalars().all()
            assert [cat.slug for cat in ordered] == ["first-order", "third-order", "second-order"]
    finally:
        _clear_overrides()


def test_delete_category_blocked_with_children_or_documents(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        parent = _insert_category(session, name="Parent", slug="parent", kind=CategoryKind.topic)
        child = _insert_category(session, name="Child", slug="child", kind=CategoryKind.topic, parent=parent)
        parent_id = parent.id
        child_id = child.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        blocked = client.delete(f"/v1/admin/categories/{parent_id}")
        assert blocked.status_code == 409

        with SessionLocal.begin() as session:
            victim = session.get(Category, child_id)
            session.delete(victim)
            doc_category = session.get(Category, parent_id)
            document = Document(
                title="Test Doc",
                type=DocumentType.article,
                lang="en",
                primary_category_id=doc_category.id,
            )
            session.add(document)

        blocked_docs = client.delete(f"/v1/admin/categories/{parent_id}")
        assert blocked_docs.status_code == 409
    finally:
        _clear_overrides()
