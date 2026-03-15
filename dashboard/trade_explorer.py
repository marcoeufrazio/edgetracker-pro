from __future__ import annotations

from dashboard.filters import TradeFilters, apply_trade_filters
from dashboard.trade_table import build_trade_table_rows
from analytics.trade_schema import NormalizedTrade


def build_filtered_trade_rows(trades: list[NormalizedTrade], filters: TradeFilters) -> list[dict[str, object]]:
    filtered_trades = apply_trade_filters(trades, filters)
    return build_trade_table_rows(filtered_trades)
