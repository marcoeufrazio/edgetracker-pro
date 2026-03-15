from __future__ import annotations

from dataclasses import dataclass

from analytics.timeline import sort_trades_by_close_time
from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class StrategyAnalyzerResult:
    average_trade_duration_minutes: float
    performance_by_duration: dict[str, float]
    performance_by_position_size: dict[float, float]
    performance_after_win_streak: dict[int, float]
    performance_after_loss_streak: dict[int, float]
    performance_by_rr: dict[str, float] | None


def analyze_strategy_patterns(trades: list[NormalizedTrade]) -> StrategyAnalyzerResult:
    ordered_trades = sort_trades_by_close_time(trades)

    if not ordered_trades:
        return StrategyAnalyzerResult(
            average_trade_duration_minutes=0.0,
            performance_by_duration={},
            performance_by_position_size={},
            performance_after_win_streak={},
            performance_after_loss_streak={},
            performance_by_rr=None,
        )

    durations = [_trade_duration_minutes(trade) for trade in ordered_trades]

    return StrategyAnalyzerResult(
        average_trade_duration_minutes=sum(durations) / len(durations),
        performance_by_duration=_aggregate_average_pnl_by_duration_bucket(ordered_trades),
        performance_by_position_size=_aggregate_average_pnl_by_position_size(ordered_trades),
        performance_after_win_streak=_aggregate_after_streak(ordered_trades, target="win"),
        performance_after_loss_streak=_aggregate_after_streak(ordered_trades, target="loss"),
        performance_by_rr=None,
    )


def _trade_duration_minutes(trade: NormalizedTrade) -> float:
    duration = trade.closed_at - trade.opened_at
    return duration.total_seconds() / 60


def _duration_bucket(duration_minutes: float) -> str:
    if duration_minutes < 15:
        return "short"
    if duration_minutes <= 60:
        return "medium"
    return "long"


def _aggregate_average_pnl_by_duration_bucket(trades: list[NormalizedTrade]) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for trade in trades:
        bucket = _duration_bucket(_trade_duration_minutes(trade))
        grouped.setdefault(bucket, []).append(trade.net_profit)
    return {bucket: sum(values) / len(values) for bucket, values in grouped.items()}


def _aggregate_average_pnl_by_position_size(trades: list[NormalizedTrade]) -> dict[float, float]:
    grouped: dict[float, list[float]] = {}
    for trade in trades:
        grouped.setdefault(trade.size_lots, []).append(trade.net_profit)
    return {size: sum(values) / len(values) for size, values in grouped.items()}


def _aggregate_after_streak(trades: list[NormalizedTrade], target: str) -> dict[int, float]:
    grouped: dict[int, list[float]] = {}
    current_wins = 0
    current_losses = 0

    for trade in trades:
        if target == "win" and current_wins > 0:
            grouped.setdefault(current_wins, []).append(trade.net_profit)
        if target == "loss" and current_losses > 0:
            grouped.setdefault(current_losses, []).append(trade.net_profit)

        if trade.net_profit > 0:
            current_wins += 1
            current_losses = 0
        elif trade.net_profit < 0:
            current_losses += 1
            current_wins = 0
        else:
            current_wins = 0
            current_losses = 0

    return {streak: sum(values) / len(values) for streak, values in grouped.items()}
