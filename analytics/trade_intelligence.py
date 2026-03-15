from __future__ import annotations

from dataclasses import dataclass

from analytics.timeline import sort_trades_by_close_time
from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class TradeIntelligence:
    best_day_of_week: str | None
    worst_day_of_week: str | None
    best_trading_hour: int | None
    worst_trading_hour: int | None
    win_rate_by_day: dict[str, float]
    best_symbol: str | None
    worst_symbol: str | None


def calculate_trade_intelligence(trades: list[NormalizedTrade]) -> TradeIntelligence:
    ordered_trades = sort_trades_by_close_time(trades)

    if not ordered_trades:
        return TradeIntelligence(
            best_day_of_week=None,
            worst_day_of_week=None,
            best_trading_hour=None,
            worst_trading_hour=None,
            win_rate_by_day={},
            best_symbol=None,
            worst_symbol=None,
        )

    day_profit_map = _group_net_profit_by_day(ordered_trades)
    hour_profit_map = _group_net_profit_by_hour(ordered_trades)
    symbol_profit_map = _group_net_profit_by_symbol(ordered_trades)

    return TradeIntelligence(
        best_day_of_week=_pick_best_key(day_profit_map),
        worst_day_of_week=_pick_worst_key(day_profit_map),
        best_trading_hour=_pick_best_key(hour_profit_map),
        worst_trading_hour=_pick_worst_key(hour_profit_map),
        win_rate_by_day=_calculate_win_rate_by_day(ordered_trades),
        best_symbol=_pick_best_key(symbol_profit_map),
        worst_symbol=_pick_worst_key(symbol_profit_map),
    )


def _group_net_profit_by_day(trades: list[NormalizedTrade]) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = {}
    for trade in trades:
        key = trade.closed_at.strftime("%A")
        grouped.setdefault(key, []).append(trade.net_profit)
    return grouped


def _group_net_profit_by_hour(trades: list[NormalizedTrade]) -> dict[int, list[float]]:
    grouped: dict[int, list[float]] = {}
    for trade in trades:
        key = trade.closed_at.hour
        grouped.setdefault(key, []).append(trade.net_profit)
    return grouped


def _group_net_profit_by_symbol(trades: list[NormalizedTrade]) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = {}
    for trade in trades:
        grouped.setdefault(trade.symbol, []).append(trade.net_profit)
    return grouped


def _pick_best_key(grouped_values: dict[object, list[float]]) -> object | None:
    if not grouped_values:
        return None

    return max(grouped_values, key=lambda key: (_average(grouped_values[key]), -len(grouped_values[key]) if isinstance(key, str) else 0, key))


def _pick_worst_key(grouped_values: dict[object, list[float]]) -> object | None:
    if not grouped_values:
        return None

    return min(grouped_values, key=lambda key: (_average(grouped_values[key]), key))


def _calculate_win_rate_by_day(trades: list[NormalizedTrade]) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for trade in trades:
        key = trade.closed_at.strftime("%A")
        grouped.setdefault(key, []).append(trade.net_profit)

    return {
        day: (sum(1 for pnl in pnl_values if pnl > 0) / len(pnl_values)) * 100
        for day, pnl_values in grouped.items()
    }


def _average(values: list[float]) -> float:
    return sum(values) / len(values)
