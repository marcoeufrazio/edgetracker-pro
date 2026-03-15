from __future__ import annotations

from analytics.equity import calculate_equity_curve
from analytics.trade_schema import EquityTimelinePoint, NormalizedTrade


def sort_trades_by_close_time(trades: list[NormalizedTrade]) -> list[NormalizedTrade]:
    return sorted(trades, key=lambda trade: (trade.closed_at, trade.ticket))


def build_trade_timeline(trades: list[NormalizedTrade], initial_balance: float) -> list[EquityTimelinePoint]:
    ordered_trades = sort_trades_by_close_time(trades)
    pnl_values = [trade.net_profit for trade in ordered_trades]
    equity_curve = calculate_equity_curve(initial_balance=initial_balance, pnl_values=pnl_values)

    timeline: list[EquityTimelinePoint] = []
    cumulative_pnl = 0.0

    for trade_number, trade in enumerate(ordered_trades, start=1):
        cumulative_pnl += trade.net_profit
        timeline.append(
            EquityTimelinePoint(
                trade_number=trade_number,
                close_time=trade.closed_at,
                pnl=trade.net_profit,
                cumulative_pnl=cumulative_pnl,
                equity=equity_curve[trade_number - 1],
            )
        )

    return timeline
