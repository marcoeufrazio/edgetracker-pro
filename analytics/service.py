from __future__ import annotations

from analytics.drawdown import calculate_drawdown
from analytics.equity import calculate_current_profit, calculate_equity_curve
from analytics.health import build_health_summary
from analytics.risk_metrics import calculate_mar_ratio, calculate_ulcer_index
from analytics.targets import calculate_green_target, calculate_traffic_light
from analytics.types import AccountMetrics


def calculate_account_metrics(
    initial_balance: float,
    pnl_values: list[float],
    cycle_target: float,
) -> AccountMetrics:
    equity = calculate_equity_curve(initial_balance=initial_balance, pnl_values=pnl_values)
    drawdown = calculate_drawdown(equity)
    ulcer_index = calculate_ulcer_index(drawdown.drawdown_pct_series)
    mar_ratio = calculate_mar_ratio(initial_balance, equity, drawdown.max_drawdown_pct)
    green_target = calculate_green_target(cycle_target)
    current_profit = calculate_current_profit(initial_balance, equity)
    traffic_light = calculate_traffic_light(current_profit=current_profit, green_target=green_target)
    health_summary = build_health_summary(
        traffic_light=traffic_light,
        current_profit=current_profit,
        green_target=green_target,
        max_drawdown_pct=drawdown.max_drawdown_pct,
        ulcer_index=ulcer_index,
    )

    return AccountMetrics(
        equity=equity,
        drawdown_abs_series=drawdown.drawdown_abs_series,
        drawdown_pct_series=drawdown.drawdown_pct_series,
        max_drawdown_abs=drawdown.max_drawdown_abs,
        max_drawdown_pct=drawdown.max_drawdown_pct,
        ulcer_index=ulcer_index,
        mar_ratio=mar_ratio,
        green_target=green_target,
        traffic_light=traffic_light,
        health_summary=health_summary,
    )
