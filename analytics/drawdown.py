from __future__ import annotations

from analytics.types import DrawdownResult


def calculate_drawdown(equity_curve: list[float]) -> DrawdownResult:
    peak = 0.0
    drawdown_abs_series: list[float] = []
    drawdown_pct_series: list[float] = []

    for equity in equity_curve:
        peak = max(peak, equity)
        drawdown_abs = peak - equity
        drawdown_pct = 0.0 if peak == 0 else (drawdown_abs / peak) * 100
        drawdown_abs_series.append(drawdown_abs)
        drawdown_pct_series.append(drawdown_pct)

    max_drawdown_abs = max(drawdown_abs_series, default=0.0)
    max_drawdown_pct = max(drawdown_pct_series, default=0.0)

    return DrawdownResult(
        drawdown_abs_series=drawdown_abs_series,
        drawdown_pct_series=drawdown_pct_series,
        max_drawdown_abs=max_drawdown_abs,
        max_drawdown_pct=max_drawdown_pct,
    )
