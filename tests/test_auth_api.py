from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import create_app


def test_auth_register_login_and_me_flow(tmp_path) -> None:
    app = create_app(database_path=tmp_path / "auth_api.db", auth_secret="test-secret")
    client = TestClient(app)

    register_response = client.post(
        "/auth/register",
        json={"email": "marco@example.com", "password": "secret123", "name": "Marco"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "marco@example.com", "password": "secret123"},
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "marco@example.com"
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "marco@example.com"
    assert me_response.json()["name"] == "Marco"


def test_auth_me_requires_valid_token(tmp_path) -> None:
    app = create_app(database_path=tmp_path / "auth_api.db", auth_secret="test-secret")
    client = TestClient(app)

    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.value"})

    assert response.status_code == 401
