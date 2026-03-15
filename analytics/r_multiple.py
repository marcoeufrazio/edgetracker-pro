from __future__ import annotations

from dataclasses import dataclass

from analytics.rr_engine import RMultipleTradeResult, calculate_trade_r_metrics
from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class RMultipleSummary:
    total_trades: int
    trades_with_r: int
    trades_without_r: int
    average_r_multiple: float
    best_r_multiple: float
    worst_r_multiple: float


def calculate_r_multiple_summary(trades: list[NormalizedTrade]) -> tuple[list[RMultipleTradeResult], RMultipleSummary]:
    trade_results = [result for result in (calculate_trade_r_metrics(trade) for trade in trades) if result is not None]

    trades_with_r = len(trade_results)
    trades_without_r = len(trades) - trades_with_r
    r_values = [result.r_multiple for result in trade_results]

    summary = RMultipleSummary(
        total_trades=len(trades),
        trades_with_r=trades_with_r,
        trades_without_r=trades_without_r,
        average_r_multiple=sum(r_values) / trades_with_r if trades_with_r else 0.0,
        best_r_multiple=max(r_values, default=0.0),
        worst_r_multiple=min(r_values, default=0.0),
    )

    return trade_results, summary
