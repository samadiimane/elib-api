from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import auth as auth_dependencies
from app.api.routes import admin_journals as admin_journals_routes
from app.main import app
from app.models.document import Document, DocumentType
from app.models.journal import Journal, JournalIssue
from app.models.user import UserRoleEnum


def _override_db(SessionLocal):
    def dependency():
        with SessionLocal() as session:
            yield session

    return dependency


def _admin_identity():
    return SimpleNamespace(
        id=1,
        email="admin@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=UserRoleEnum.admin)],
    )


def _non_admin_identity():
    return SimpleNamespace(
        id=2,
        email="viewer@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=UserRoleEnum.researcher)],
    )


def _apply_overrides(SessionLocal, identity):
    app.dependency_overrides[admin_journals_routes.get_db] = _override_db(SessionLocal)
    app.dependency_overrides[auth_dependencies.get_current_user] = lambda: identity


def _clear_overrides():
    app.dependency_overrides.pop(admin_journals_routes.get_db, None)
    app.dependency_overrides.pop(auth_dependencies.get_current_user, None)


def test_admin_journal_issues_requires_admin(head_database):
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        journal = Journal(name="Atlas", slug="atlas")
        session.add(journal)
        session.flush()
        journal_id = journal.id

    _apply_overrides(SessionLocal, _non_admin_identity())
    client = TestClient(app)
    try:
        response = client.get(f"/v1/admin/journals/{journal_id}/issues")
        assert response.status_code == 403
    finally:
        _clear_overrides()


def test_list_journal_issues_filters_and_sorts(head_database):
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        journal = Journal(name="Atlas", slug="atlas")
        session.add(journal)
        session.flush()
        journal_id = journal.id

        issue1 = JournalIssue(journal_id=journal_id, volume=1, number=1, year=2023, title="Maps 2023")
        issue2 = JournalIssue(journal_id=journal_id, volume=1, number=2, year=2024, title="Desert 2024")
        session.add_all([issue1, issue2])
        session.flush()

        # one article in issue2
        session.add(
            Document(
                title="Article in issue 2",
                type=DocumentType.article,
                lang="en",
                journal_id=journal_id,
                issue_id=issue2.id,
            )
        )

    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        response = client.get(
            f"/v1/admin/journals/{journal_id}/issues",
            params={"sort": "year_desc", "page_size": 10},
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["total"] == 2
        assert payload["items"][0]["year"] == 2024
        assert payload["items"][0]["articles_count"] == 1

        by_number = client.get(
            f"/v1/admin/journals/{journal_id}/issues",
            params={"sort": "number_asc", "page_size": 10},
        )
        assert by_number.status_code == 200
        assert by_number.json()["items"][0]["number"] == 1

        filtered = client.get(
            f"/v1/admin/journals/{journal_id}/issues",
            params={"year": 2023, "q": "Maps"},
        )
        assert filtered.status_code == 200
        filtered_items = filtered.json()["items"]
        assert len(filtered_items) == 1
        assert filtered_items[0]["year"] == 2023
    finally:
        _clear_overrides()


def test_issue_crud_and_delete_guard(head_database):
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        journal = Journal(name="CRUD", slug="crud")
        session.add(journal)
        session.flush()
        journal_id = journal.id

    _apply_overrides(SessionLocal, _admin_identity())
    client = TestClient(app)
    try:
        # create
        resp = client.post(
            f"/v1/admin/journals/{journal_id}/issues",
            json={"year": 2024, "number": 1, "title": "Vol 1"},
        )
        assert resp.status_code == 201, resp.text
        issue = resp.json()
        issue_id = issue["id"]

        # duplicate
        dup = client.post(
            f"/v1/admin/journals/{journal_id}/issues",
            json={"year": 2024, "number": 1, "title": "Dup"},
        )
        assert dup.status_code == 409

        # update
        upd = client.patch(f"/v1/admin/issues/{issue_id}", json={"title": "Updated"})
        assert upd.status_code == 200
        assert upd.json()["title"] == "Updated"

        # block delete when articles
        with SessionLocal.begin() as session:
            session.add(
                Document(
                    title="Article",
                    type=DocumentType.article,
                    lang="en",
                    journal_id=journal_id,
                    issue_id=issue_id,
                )
            )
        blocked = client.delete(f"/v1/admin/issues/{issue_id}")
        assert blocked.status_code == 409

        # allow delete when no articles
        with SessionLocal.begin() as session:
            session.execute(
                select(Document)
                .where(Document.issue_id == issue_id)
                .with_for_update()
            )
            session.query(Document).filter(Document.issue_id == issue_id).delete()
        allowed = client.delete(f"/v1/admin/issues/{issue_id}")
        assert allowed.status_code == 200
        assert allowed.json()["ok"] is True
    finally:
        _clear_overrides()


def test_repository_list_issues_constant_queries(head_database):
    SessionLocal, engine = head_database
    with SessionLocal.begin() as session:
        journal = Journal(name="Perf", slug="perf")
        session.add(journal)
        session.flush()
        journal_id = journal.id
        for i in range(10):
            issue = JournalIssue(journal_id=journal_id, number=i + 1, year=2020 + i, title=f"Issue {i}")
            session.add(issue)
            session.flush()
            session.add(
                Document(
                    title=f"Article {i}",
                    type=DocumentType.article,
                    lang="en",
                    journal_id=journal_id,
                    issue_id=issue.id,
                )
            )

    counter = {"count": 0}

    def _count_queries(_conn, _cursor, _statement, _params, _context, _executemany):
        counter["count"] += 1

    from app.repositories.admin_journals import JournalAdminRepository

    from sqlalchemy import event

    event.listen(engine, "before_cursor_execute", _count_queries)
    try:
        with SessionLocal() as session:
            repo = JournalAdminRepository(session)
            payload = repo.list_issues(
                journal_id=journal_id,
                q=None,
                year=None,
                page=1,
                page_size=5,
                sort="year_desc",
            )
            assert payload.total == 10
            assert len(payload.items) == 5
            assert payload.items[0].articles_count == 1
    finally:
        event.remove(engine, "before_cursor_execute", _count_queries)

    # expect only two queries (count + page)
    assert counter["count"] <= 3
