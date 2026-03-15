from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from api import routes_accounts


SAMPLE_SOURCE_PATH = Path("data/imports/mt4_statement.htm")


def test_upload_statement_saves_file_and_returns_account_id(tmp_path, monkeypatch) -> None:
    _configure_statement_dirs(tmp_path, monkeypatch)
    client = TestClient(app)

    response = client.post(
        "/upload-statement",
        files={"file": ("uploaded_statement.htm", SAMPLE_SOURCE_PATH.read_bytes(), "text/html")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["account_id"] == "24601985"
    assert Path(payload["statement_path"]).exists()


def test_analyze_account_returns_pipeline_metrics() -> None:
    client = TestClient(app)

    response = client.post(
        "/analyze-account",
        json={
            "statement_path": "data/imports/mt4_statement.html",
            "initial_balance": 1000.0,
            "cycle_target": 200.0,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["performance"]["total_trades"] == 247
    assert payload["account_metrics"]["traffic_light"] == "red"
    assert payload["current_risk_zone"] in {"green", "yellow", "red"}
    assert len(payload["equity_timeline"]) == len(payload["drawdown_series"])


def test_dashboard_endpoint_loads_account_by_account_id(tmp_path, monkeypatch) -> None:
    account_id = _copy_sample_statement(tmp_path, monkeypatch)
    client = TestClient(app)

    response = client.get(f"/dashboard/{account_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["account_id"] == account_id
    assert payload["performance"]["total_trades"] == 247
    assert payload["drawdown_series"][-1]["risk_zone"] == payload["current_risk_zone"]


def test_report_endpoint_returns_summary_markdown(tmp_path, monkeypatch) -> None:
    account_id = _copy_sample_statement(tmp_path, monkeypatch)
    client = TestClient(app)

    response = client.get(f"/report/{account_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["health_score"]["health_classification"]
    assert "EdgeTracker-Pro Report Summary" in payload["report_summary_markdown"]
    assert payload["metrics_summary"]["total_trades"] == 247


def test_accounts_comparison_returns_table_and_ranking(tmp_path, monkeypatch) -> None:
    _copy_sample_statement(tmp_path, monkeypatch)
    client = TestClient(app)

    response = client.get("/accounts/comparison")

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
