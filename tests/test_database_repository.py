from __future__ import annotations

from datetime import datetime

from analytics.trade_schema import NormalizedTrade
from analytics.types import AccountMetrics
from database.db import connect_db, initialize_db
from database.repository import Repository


def _make_trade(ticket: int, pnl: float) -> NormalizedTrade:
    return NormalizedTrade(
        ticket=ticket,
        opened_at=datetime(2026, 3, 1, 9, 0, 0),
        closed_at=datetime(2026, 3, 1, 10, 0, 0),
        side="buy",
        size_lots=0.01,
        symbol="EURUSD",
        open_price=1.1,
        stop_loss=None,
        take_profit=None,
        close_price=1.1005,
        commission=0.0,
        taxes=0.0,
        swap=0.0,
        profit=pnl,
        net_profit=pnl,
        source="mt4_html",
        source_type="buy",
    )


def _make_metrics() -> AccountMetrics:
    return AccountMetrics(
        equity=[1010.0, 1005.0],
        drawdown_abs_series=[0.0, 5.0],
        drawdown_pct_series=[0.0, 0.5],
        max_drawdown_abs=5.0,
        max_drawdown_pct=0.5,
        ulcer_index=0.3535,
        mar_ratio=2.0,
        green_target=75.0,
        traffic_light="green",
        health_summary="Status=green",
    )


def test_repository_creates_reads_and_counts_entities(tmp_path) -> None:
    connection = connect_db(tmp_path / "edgetracker.db")
    initialize_db(connection)
    repository = Repository(connection)

    user = repository.create_user("Marco", "marco@example.com")
    account = repository.create_account(user.id, "24601985", broker="VT Markets", currency="USD")
    trades = repository.save_trades(account.id, [_make_trade(1, 10.0), _make_trade(2, -5.0)])
    metric_records = repository.save_metrics(account.id, _make_metrics())
    report = repository.save_report(
        account.id,
        report_name="account_summary",
        content="# EdgeTracker-Pro Report",
    )

    stored_accounts = repository.list_accounts(user.id)
    stored_trades = repository.list_trades(account.id)
    stored_metrics = repository.get_account_metrics(account.id)
    stored_reports = repository.list_reports(account.id)

    assert user.id is not None
    assert account.id is not None
    assert len(trades) == 2
    assert len(metric_records) == 10
    assert report.report_name == "account_summary"
    assert len(stored_accounts) == 1
    assert len(stored_trades) == 2
    assert stored_metrics["traffic_light"] == "green"
    assert stored_metrics["equity"] == [1010.0, 1005.0]
    assert len(stored_reports) == 1
    assert repository.count_rows("users") == 1
    assert repository.count_rows("accounts") == 1
    assert repository.count_rows("trades") == 2
    assert repository.count_rows("metrics") == 10
    assert repository.count_rows("reports") == 1


def test_save_account_metrics_keeps_legacy_summary_subset(tmp_path) -> None:
    connection = connect_db(tmp_path / "edgetracker.db")
    initialize_db(connection)
    repository = Repository(connection)

    user = repository.create_user("Marco", "marco@example.com")
    account = repository.create_account(user.id, "24601985")

    records = repository.save_account_metrics(account.id, _make_metrics())
    stored_metrics = repository.get_account_metrics(account.id)

    assert len(records) == 5
    assert sorted(stored_metrics) == [
        "green_target",
        "mar_ratio",
        "max_drawdown_abs",
        "max_drawdown_pct",
        "ulcer_index",
    ]
