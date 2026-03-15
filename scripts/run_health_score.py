from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.drawdown_series import build_drawdown_series_from_mt4_statement
from analytics.health_diagnostics import build_health_diagnostic_text
from analytics.health_score import calculate_health_score
from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.performance import calculate_performance_metrics
from analytics.service import calculate_account_metrics


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    pnl_values = [trade.net_profit for trade in normalized_trades]

    performance = calculate_performance_metrics(normalized_trades)
    account_metrics = calculate_account_metrics(
        initial_balance=1000.0,
        pnl_values=pnl_values,
        cycle_target=50.0,
    )
    drawdown_series = build_drawdown_series_from_mt4_statement(
        path=statement_path,
        initial_balance=1000.0,
    )
    current_risk_zone = drawdown_series[-1].risk_zone if drawdown_series else "green"

    score = calculate_health_score(
        profit_factor=performance.profit_factor,
        expectancy=performance.expectancy,
        max_drawdown_pct=account_metrics.max_drawdown_pct,
        ulcer_index=account_metrics.ulcer_index,
        risk_zone=current_risk_zone,
        traffic_light=account_metrics.traffic_light,
    )
    diagnostic_text = build_health_diagnostic_text(
        health_classification=score.health_classification,
        profit_factor=performance.profit_factor,
        expectancy=performance.expectancy,
        max_drawdown_pct=account_metrics.max_drawdown_pct,
        ulcer_index=account_metrics.ulcer_index,
        risk_zone=current_risk_zone,
        traffic_light=account_metrics.traffic_light,
    )

    print("EdgeTracker-Pro Module 7 Health Score")
    print(f"Health Score: {score.health_score}")
    print(f"Health Classification: {score.health_classification}")
    print(f"Health Diagnostic: {diagnostic_text}")


if __name__ == "__main__":
    main()
