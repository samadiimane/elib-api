from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import auth as auth_dependencies
from app.api.routes import admin as admin_routes
from app.main import app
from app.models.user import User, UserRoleEnum
from app.services.auth import create_user_with_password


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
    app.dependency_overrides[admin_routes.get_db] = _override_db(SessionLocal)
    app.dependency_overrides[auth_dependencies.get_current_user] = lambda: _admin_identity()


def _clear_overrides():
    app.dependency_overrides.pop(admin_routes.get_db, None)
    app.dependency_overrides.pop(auth_dependencies.get_current_user, None)


def test_admin_create_user_enforces_uniqueness(head_database) -> None:
    SessionLocal, _engine = head_database
    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        payload = {
            "email": "new-admin@example.org",
            "password": "Str0ngPass!",
            "roles": ["admin", "researcher"],
        }
        response = client.post("/v1/admin/users", json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["email"] == "new-admin@example.org"
        assert data["is_active"] is True
        assert data["roles"] == ["admin", "researcher"]

        duplicate = client.post("/v1/admin/users", json=payload)
        assert duplicate.status_code == 400

        with SessionLocal() as session:
            created = session.execute(
                select(User).where(User.email == "new-admin@example.org")
            ).scalar_one()
            assert created.is_active is True
            assert {role.role.value for role in created.roles} == {"admin", "researcher"}
    finally:
        _clear_overrides()


def test_admin_list_users_supports_filters(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        create_user_with_password(
            session,
            email="researcher@example.org",
            password="Password123!",
            roles=[UserRoleEnum.researcher],
        )
        create_user_with_password(
            session,
            email="committee@example.org",
            password="Password123!",
            roles=[UserRoleEnum.committee],
        )
        create_user_with_password(
            session,
            email="MIXEDCASE@Example.org",
            password="Password123!",
            roles=[UserRoleEnum.admin],
        )

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        paged = client.get("/v1/admin/users", params={"page_size": 1})
        assert paged.status_code == 200
        payload = paged.json()
        assert payload["total"] == 3
        assert len(payload["items"]) == 1
        assert payload["page"] == 1
        assert payload["page_size"] == 1

        by_role = client.get("/v1/admin/users", params={"role": "committee"})
        assert by_role.status_code == 200
        role_payload = by_role.json()
        assert role_payload["total"] == 1
        assert role_payload["items"][0]["email"] == "committee@example.org"

        search = client.get("/v1/admin/users", params={"q": "mixedcase"})
        assert search.status_code == 200
        search_payload = search.json()
        assert search_payload["total"] == 1
        assert search_payload["items"][0]["email"] == "mixedcase@example.org"
    finally:
        _clear_overrides()


def test_admin_replace_roles_and_toggle_active(head_database) -> None:
    SessionLocal, _engine = head_database
    with SessionLocal.begin() as session:
        user = create_user_with_password(
            session,
            email="subject@example.org",
            password="Password123!",
            roles=[UserRoleEnum.researcher],
        )
        user_id = user.id

    _apply_admin_overrides(SessionLocal)
    try:
        client = TestClient(app)
        replace = client.patch(
            f"/v1/admin/users/{user_id}/roles",
            json={"roles": ["admin", "committee"]},
        )
        assert replace.status_code == 200, replace.text
        replace_payload = replace.json()
        assert replace_payload["roles"] == ["admin", "committee"]

        toggle = client.patch(
            f"/v1/admin/users/{user_id}/active",
            json={"is_active": False},
        )
        assert toggle.status_code == 200
        toggle_payload = toggle.json()
        assert toggle_payload["is_active"] is False

        with SessionLocal() as session:
            db_user = session.execute(select(User).where(User.id == user_id)).scalar_one()
            assert db_user.is_active is False
            assert {role.role.value for role in db_user.roles} == {"admin", "committee"}
    finally:
        _clear_overrides()
