from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.main import create_app
from api import routes_accounts
from database.db import connect_db, initialize_db
from database.repository import Repository


SAMPLE_SOURCE_PATH = Path("data/imports/mt4_statement.htm")


def test_upload_statement_saves_file_and_returns_account_id(tmp_path, monkeypatch) -> None:
    _configure_statement_dirs(tmp_path, monkeypatch)
    app = create_app(database_path=tmp_path / "api.db", auth_secret="test-secret")
    client = TestClient(app)

    response = client.post(
        "/upload-statement",
        files={"file": ("uploaded_statement.htm", SAMPLE_SOURCE_PATH.read_bytes(), "text/html")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["account_id"] == "24601985"
    assert Path(payload["statement_path"]).exists()


def test_analyze_account_returns_pipeline_metrics(tmp_path) -> None:
    app = create_app(database_path=tmp_path / "api.db", auth_secret="test-secret")
    client = TestClient(app)
    token = _register_and_login(client, "marco.analysis@example.com")
    _seed_owned_account(app, "marco.analysis@example.com", "24601985")

    response = client.post(
        "/analyze-account",
        json={
            "account_id": "24601985",
            "initial_balance": 1000.0,
            "cycle_target": 200.0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["performance"]["total_trades"] == 247
    assert payload["account_metrics"]["traffic_light"] == "red"
    assert payload["current_risk_zone"] in {"green", "yellow", "red"}
    assert len(payload["equity_timeline"]) == len(payload["drawdown_series"])


def test_dashboard_endpoint_loads_account_by_account_id(tmp_path, monkeypatch) -> None:
    account_id = _copy_sample_statement(tmp_path, monkeypatch)
    app = create_app(database_path=tmp_path / "api.db", auth_secret="test-secret")
    client = TestClient(app)
    token = _register_and_login(client, "marco.dashboard@example.com")
    _seed_owned_account(app, "marco.dashboard@example.com", account_id, statement_path=str(routes_accounts.STATEMENTS_DIR / "mt4_statement.htm"))

    response = client.get(f"/dashboard/{account_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["account_id"] == account_id
    assert payload["performance"]["total_trades"] == 247
    assert payload["drawdown_series"][-1]["risk_zone"] == payload["current_risk_zone"]


def test_report_endpoint_returns_summary_markdown(tmp_path, monkeypatch) -> None:
    account_id = _copy_sample_statement(tmp_path, monkeypatch)
    app = create_app(database_path=tmp_path / "api.db", auth_secret="test-secret")
    client = TestClient(app)
    token = _register_and_login(client, "marco.report@example.com")
    _seed_owned_account(app, "marco.report@example.com", account_id, statement_path=str(routes_accounts.STATEMENTS_DIR / "mt4_statement.htm"))

    response = client.get(f"/report/{account_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["health_score"]["health_classification"]
    assert "EdgeTracker-Pro Report Summary" in payload["report_summary_markdown"]
    assert payload["metrics_summary"]["total_trades"] == 247


def test_accounts_comparison_returns_table_and_ranking(tmp_path, monkeypatch) -> None:
    _copy_sample_statement(tmp_path, monkeypatch)
    app = create_app(database_path=tmp_path / "api.db", auth_secret="test-secret")
    client = TestClient(app)
    token = _register_and_login(client, "marco.compare@example.com")
    _seed_owned_account(app, "marco.compare@example.com", "24601985", statement_path=str(routes_accounts.STATEMENTS_DIR / "mt4_statement.htm"))

    response = client.get("/accounts/comparison", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["aggregated_metrics"]["total_accounts"] == 1
    assert payload["comparison_table"][0]["account_id"] == "24601985"
    assert payload["performance_ranking"][0]["rank"] == 1


def _configure_statement_dirs(tmp_path: Path, monkeypatch) -> Path:
    statements_dir = tmp_path / "imports"
    uploads_dir = statements_dir / "uploads"
    statements_dir.mkdir(parents=True, exist_ok=True)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(routes_accounts, "STATEMENTS_DIR", statements_dir)
    monkeypatch.setattr(routes_accounts, "UPLOADS_DIR", uploads_dir)
    return statements_dir


def _copy_sample_statement(tmp_path: Path, monkeypatch) -> str:
    statements_dir = _configure_statement_dirs(tmp_path, monkeypatch)
    target_path = statements_dir / "mt4_statement.htm"
    target_path.write_bytes(SAMPLE_SOURCE_PATH.read_bytes())
    return "24601985"


def _register_and_login(client: TestClient, email: str) -> str:
    client.post(
        "/auth/register",
        json={"email": email, "password": "secret123", "name": "Marco"},
    )
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "secret123"},
    )
    return response.json()["access_token"]


def _seed_owned_account(app, email: str, account_ref: str, statement_path: str = "data/imports/mt4_statement.htm") -> None:
    db_connection = connect_db(app.state.database_path)
    initialize_db(db_connection)
    repository = Repository(db_connection)
    row = db_connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    repository.save_account(
        user_id=int(row["id"]),
        account_ref=account_ref,
        statement_path=statement_path,
    )
    db_connection.close()
