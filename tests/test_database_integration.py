from __future__ import annotations

from pathlib import Path

from analytics.report_builder import build_report_bundle
from analytics.report_formatter import format_report_summary_markdown
from dashboard.data_loader import load_dashboard_data
from database.db import connect_db, initialize_db
from database.repository import Repository


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_database_integration_persists_pipeline_outputs(tmp_path) -> None:
    connection = connect_db(tmp_path / "edgetracker.db")
    initialize_db(connection)
    repository = Repository(connection)

    dashboard_data = load_dashboard_data(SAMPLE_STATEMENT_PATH)
    report_bundle = build_report_bundle(SAMPLE_STATEMENT_PATH)
    report_markdown = format_report_summary_markdown(report_bundle)

    user = repository.create_user("Marco", "marco@example.com")
    account = repository.create_account(user.id, "MT4-DEMO", broker="MT4", currency="USD")
    saved_trades = repository.save_trades(account.id, dashboard_data.normalized_trades)
    saved_metrics = repository.save_metrics(account.id, dashboard_data.account_metrics)
    saved_report = repository.save_report(
        account.id,
        report_name="report_summary",
        report_type="markdown",
        generated_at=report_bundle.generated_at,
        content=report_markdown,
    )

    stored_accounts = repository.list_accounts(user.id)
    stored_metrics = repository.get_account_metrics(account.id)
    stored_reports = repository.list_reports(account.id)

    assert len(saved_trades) == len(dashboard_data.normalized_trades)
    assert len(saved_metrics) == 10
    assert saved_report.content.startswith("# EdgeTracker-Pro Report Summary")
    assert len(stored_accounts) == 1
    assert stored_metrics["traffic_light"] == dashboard_data.account_metrics.traffic_light
    assert stored_metrics["health_summary"] == dashboard_data.account_metrics.health_summary
    assert stored_metrics["max_drawdown_pct"] == dashboard_data.account_metrics.max_drawdown_pct
    assert len(stored_reports) == 1
    assert "Health Diagnostic" in stored_reports[0].content
