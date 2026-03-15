from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class TradeFilters:
    symbol: str = "all"
    result_type: str = "all"
    day_of_week: str = "all"
    hour_of_day: int | str = "all"
    date_from: date | None = None
    date_to: date | None = None


def apply_trade_filters(trades: list[NormalizedTrade], filters: TradeFilters) -> list[NormalizedTrade]:
    filtered_trades = trades

    if filters.symbol != "all":
        filtered_trades = [trade for trade in filtered_trades if trade.symbol == filters.symbol]

    if filters.result_type == "wins":
        filtered_trades = [trade for trade in filtered_trades if trade.net_profit > 0]
    elif filters.result_type == "losses":
        filtered_trades = [trade for trade in filtered_trades if trade.net_profit < 0]

    if filters.day_of_week != "all":
        filtered_trades = [trade for trade in filtered_trades if trade.closed_at.strftime("%A") == filters.day_of_week]

    if filters.hour_of_day != "all":
        filtered_trades = [trade for trade in filtered_trades if trade.closed_at.hour == filters.hour_of_day]

    if filters.date_from is not None:
        filtered_trades = [trade for trade in filtered_trades if trade.closed_at.date() >= filters.date_from]

    if filters.date_to is not None:
        filtered_trades = [trade for trade in filtered_trades if trade.closed_at.date() <= filters.date_to]

    return filtered_trades


def get_filter_options(trades: list[NormalizedTrade]) -> dict[str, list[object]]:
    symbols = sorted({trade.symbol for trade in trades})
    days = sorted({trade.closed_at.strftime("%A") for trade in trades})
    hours = sorted({trade.closed_at.hour for trade in trades})

    return {
        "symbols": ["all", *symbols],
        "result_types": ["all", "wins", "losses"],
        "days_of_week": ["all", *days],
        "hours_of_day": ["all", *hours],
    }
