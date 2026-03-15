from types import SimpleNamespace

from analytics.account_comparison import build_account_comparison
from analytics.multi_account import AccountAnalysis


def _make_account(account_id: str, total_trades: int, win_rate: float, profit_factor: float, net_profit: float, max_drawdown_pct: float, health_score: int) -> AccountAnalysis:
    dashboard_data = SimpleNamespace(
        performance=SimpleNamespace(
            total_trades=total_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            net_profit=net_profit,
        ),
        account_metrics=SimpleNamespace(
            max_drawdown_pct=max_drawdown_pct,
            traffic_light="green",
        ),
        current_risk_zone="green",
    )
    return AccountAnalysis(
        account_id=account_id,
        statement_path=f"{account_id}.html",
        dashboard_data=dashboard_data,
        health_score=health_score,
        health_classification="good",
    )


def test_build_account_comparison_returns_table_aggregates_and_ranking() -> None:
    accounts = [
        _make_account("A1", 10, 60.0, 1.2, 50.0, 5.0, 70),
        _make_account("A2", 8, 55.0, 0.9, -10.0, 12.0, 40),
    ]

    comparison = build_account_comparison(accounts)

    assert len(comparison.comparison_table) == 2
    assert comparison.aggregated_metrics["total_accounts"] == 2
    assert comparison.aggregated_metrics["total_trades"] == 18
    assert comparison.aggregated_metrics["best_account"] == "A1"
    assert comparison.aggregated_metrics["worst_account"] == "A2"
    assert comparison.performance_ranking[0]["account_id"] == "A1"
    assert comparison.performance_ranking[1]["account_id"] == "A2"
