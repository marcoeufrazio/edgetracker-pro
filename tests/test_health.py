from analytics.health import build_health_summary
from analytics.service import calculate_account_metrics


def test_build_health_summary_contains_core_fields() -> None:
    summary = build_health_summary(
        traffic_light="yellow",
        current_profit=180.0,
        green_target=300.0,
        max_drawdown_pct=5.25,
        ulcer_index=3.10,
    )

    assert "Status=yellow" in summary
    assert "profit=180.00" in summary
    assert "green_target=300.00" in summary
    assert "max_drawdown_pct=5.25" in summary
    assert "ulcer_index=3.10" in summary


def test_calculate_account_metrics_returns_full_module_one_output() -> None:
    metrics = calculate_account_metrics(
        initial_balance=1000.0,
        pnl_values=[100.0, -50.0, 200.0, -25.0],
        cycle_target=150.0,
    )

    assert metrics.equity == [1100.0, 1050.0, 1250.0, 1225.0]
    assert metrics.drawdown_abs_series == [0.0, 50.0, 0.0, 25.0]
    assert metrics.max_drawdown_abs == 50.0
    assert metrics.green_target == 225.0
    assert metrics.traffic_light == "green"
    assert metrics.ulcer_index > 0
    assert metrics.mar_ratio > 0
    assert "Status=green" in metrics.health_summary
