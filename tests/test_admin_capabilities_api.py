from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import auth as auth_dependencies
from app.api.routes import admin_capabilities as admin_capabilities_routes
from app.main import app
from app.models.user import UserRoleEnum


def _mock_identity(role: UserRoleEnum):
    return SimpleNamespace(
        id=42,
        email="capability-tester@example.org",
        is_active=True,
        roles=[SimpleNamespace(role=role)],
    )


def _override_user(role: UserRoleEnum):
    app.dependency_overrides[auth_dependencies.get_current_user] = lambda: _mock_identity(role)


def _clear_overrides():
    app.dependency_overrides.pop(auth_dependencies.get_current_user, None)


def test_admin_capabilities_requires_admin_like_role():
    _override_user(UserRoleEnum.researcher)
    client = TestClient(app)
    try:
        response = client.get("/v1/admin/capabilities")
        assert response.status_code == 403
    finally:
        _clear_overrides()


def test_admin_capabilities_returns_static_payload_for_admin_roles():
    for role in (UserRoleEnum.admin, UserRoleEnum.committee):
        _override_user(role)
        client = TestClient(app)
        try:
            response = client.get("/v1/admin/capabilities")
            assert response.status_code == 200
            payload = response.json()
            assert payload == admin_capabilities_routes.DEFAULT_ADMIN_CAPABILITIES.model_dump()
            assert payload["authors"] == {
                "list": True,
                "create": True,
                "update": False,
                "delete": False,
            }
        finally:
            _clear_overrides()
