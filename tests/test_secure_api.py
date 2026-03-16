from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import create_app
from database.db import connect_db, initialize_db
from database.repository import Repository


def test_protected_endpoints_allow_only_owner_access(tmp_path) -> None:
    app = create_app(database_path=tmp_path / "secure_api.db", auth_secret="test-secret")
    client = TestClient(app)

    owner_token = _register_and_login(client, "owner@example.com", "secret123", "Owner")
    other_token = _register_and_login(client, "other@example.com", "secret123", "Other")
    _seed_owned_account(app.state.database_path, owner_email="owner@example.com", account_ref="24601985")

    analyze_response = client.post(
        "/analyze-account",
        json={"account_id": "24601985", "initial_balance": 1000.0, "cycle_target": 200.0},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    dashboard_response = client.get(
        "/dashboard/24601985",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    report_response = client.get(
        "/report/24601985",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    comparison_response = client.get(
        "/accounts/comparison",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    forbidden_response = client.get(
        "/dashboard/24601985",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert analyze_response.status_code == 200
    assert dashboard_response.status_code == 200
    assert report_response.status_code == 200
    assert comparison_response.status_code == 200
    assert comparison_response.json()["aggregated_metrics"]["total_accounts"] == 1
    assert forbidden_response.status_code == 403


def test_protected_endpoints_require_authentication(tmp_path) -> None:
    app = create_app(database_path=tmp_path / "secure_api.db", auth_secret="test-secret")
    client = TestClient(app)

    response = client.get("/accounts/comparison")

    assert response.status_code == 401


def _register_and_login(client: TestClient, email: str, password: str, name: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password, "name": name})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def _seed_owned_account(database_path, owner_email: str, account_ref: str) -> None:
    connection = connect_db(database_path)
    initialize_db(connection)
    repository = Repository(connection)
    user_row = connection.execute("SELECT id FROM users WHERE email = ?", (owner_email,)).fetchone()
    repository.save_account(
        user_id=int(user_row["id"]),
        account_ref=account_ref,
        broker="MT4",
        currency="USD",
        statement_path="data/imports/mt4_statement.htm",
    )
    connection.close()
