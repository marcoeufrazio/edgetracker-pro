from __future__ import annotations

from analytics.rr_engine import calculate_trade_r_metrics
from analytics.trade_schema import NormalizedTrade


def build_trade_table_rows(trades: list[NormalizedTrade]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for trade in trades:
        r_result = calculate_trade_r_metrics(trade)
        duration_minutes = (trade.closed_at - trade.opened_at).total_seconds() / 60

        row: dict[str, object] = {
            "ticket": trade.ticket,
            "symbol": trade.symbol,
            "type": trade.side,
            "open_time": trade.opened_at.isoformat(sep=" "),
            "close_time": trade.closed_at.isoformat(sep=" "),
            "pnl": round(trade.net_profit, 4),
            "volume": trade.size_lots,
            "duration_minutes": round(duration_minutes, 2),
        }

        if r_result is not None:
            row["r_multiple"] = round(r_result.r_multiple, 4)

        rows.append(row)

    return rows
