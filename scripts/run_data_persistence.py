from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.report_builder import build_report_bundle
from analytics.report_formatter import format_report_summary_markdown
from dashboard.data_loader import load_dashboard_data
from database.db import DEFAULT_DATABASE_NAME, connect_db, initialize_db
from database.repository import Repository


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    database_path = PROJECT_ROOT / "data" / DEFAULT_DATABASE_NAME

    connection = connect_db(database_path)
    initialize_db(connection)
    repository = Repository(connection)

    dashboard_data = load_dashboard_data(statement_path)
    report_bundle = build_report_bundle(statement_path)
    report_markdown = format_report_summary_markdown(report_bundle)
    run_id = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    user = repository.create_user("Demo User", f"demo.user+{run_id}@example.com")
    account = repository.create_account(user.id, f"MT4-DEMO-{run_id}", broker="MetaTrader 4", currency="USD")
    repository.save_trades(account.id, dashboard_data.normalized_trades)
    repository.save_metrics(account.id, dashboard_data.account_metrics)
    repository.save_report(
        account.id,
        report_name="report_summary",
        report_type="markdown",
        generated_at=report_bundle.generated_at,
        content=report_markdown,
    )

    stored_accounts = repository.list_accounts(user.id)
    stored_metrics = repository.get_account_metrics(account.id)

    print("EdgeTracker-Pro Module 15 Data Persistence")
    print(f"Database: {database_path}")
    print(f"Accounts saved: {len(stored_accounts)}")
    print(f"Trades saved: {repository.count_rows('trades')}")
    print(f"Metrics saved: {repository.count_rows('metrics')}")
    print(f"Reports saved: {repository.count_rows('reports')}")
    print(f"Traffic light: {stored_metrics['traffic_light']}")
    print(f"Health summary: {stored_metrics['health_summary']}")


if __name__ == "__main__":
    main()
