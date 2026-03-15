from pathlib import Path

import pytest

from dashboard.data_loader import load_dashboard_data


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_load_dashboard_data_returns_expected_pipeline_outputs() -> None:
    data = load_dashboard_data(SAMPLE_STATEMENT_PATH, initial_balance=1000.0, cycle_target=200.0)

    assert data.performance.total_trades == 247
    assert data.account_metrics.traffic_light == "red"
    assert data.current_risk_zone in {"green", "yellow", "red"}
    assert data.current_drawdown_pct == pytest.approx(data.drawdown_series[-1].drawdown_pct)
    assert len(data.equity_timeline) == len(data.drawdown_series)
    assert data.account_metrics.equity[-1] == pytest.approx(data.equity_timeline[-1].equity)


def test_load_dashboard_data_derives_cycle_target_when_missing() -> None:
    data = load_dashboard_data(SAMPLE_STATEMENT_PATH, initial_balance=1000.0)

    assert data.account_metrics.green_target == pytest.approx(75.0)
