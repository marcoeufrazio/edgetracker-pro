from __future__ import annotations

from pathlib import Path

from analytics.drawdown import calculate_drawdown
from analytics.equity_builder import build_equity_timeline_from_mt4_statement
from analytics.risk_zones import classify_risk_zone
from analytics.trade_schema import DrawdownTimelinePoint, EquityTimelinePoint


def build_drawdown_series(timeline: list[EquityTimelinePoint]) -> list[DrawdownTimelinePoint]:
    equity_curve = [point.equity for point in timeline]
    drawdown = calculate_drawdown(equity_curve)

    peak_equity = 0.0
    drawdown_timeline: list[DrawdownTimelinePoint] = []

    for index, point in enumerate(timeline):
        peak_equity = max(peak_equity, point.equity)
        drawdown_pct = drawdown.drawdown_pct_series[index]

        drawdown_timeline.append(
            DrawdownTimelinePoint(
                trade_number=point.trade_number,
                close_time=point.close_time,
                pnl=point.pnl,
                cumulative_pnl=point.cumulative_pnl,
                equity=point.equity,
                peak_equity=peak_equity,
                drawdown_abs=drawdown.drawdown_abs_series[index],
                drawdown_pct=drawdown_pct,
                risk_zone=classify_risk_zone(drawdown_pct),
            )
        )

    return drawdown_timeline


def build_drawdown_series_from_mt4_statement(
    path: str | Path,
    initial_balance: float,
) -> list[DrawdownTimelinePoint]:
    timeline = build_equity_timeline_from_mt4_statement(
        path=path,
        initial_balance=initial_balance,
    )
    return build_drawdown_series(timeline)
