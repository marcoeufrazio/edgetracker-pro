from __future__ import annotations

from pathlib import Path

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.timeline import build_trade_timeline
from analytics.trade_schema import EquityTimelinePoint, NormalizedTrade


def build_equity_timeline_from_trades(
    trades: list[NormalizedTrade],
    initial_balance: float,
) -> list[EquityTimelinePoint]:
    return build_trade_timeline(trades=trades, initial_balance=initial_balance)


def build_equity_timeline_from_mt4_statement(
    path: str | Path,
    initial_balance: float,
) -> list[EquityTimelinePoint]:
    imported_trades = import_mt4_closed_trades(path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    return build_equity_timeline_from_trades(
        trades=normalized_trades,
        initial_balance=initial_balance,
    )
