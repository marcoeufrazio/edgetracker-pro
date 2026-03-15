from __future__ import annotations

from dataclasses import dataclass

from analytics.timeline import sort_trades_by_close_time
from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class TradeStreaks:
    max_consecutive_wins: int
    max_consecutive_losses: int


def calculate_trade_streaks(trades: list[NormalizedTrade]) -> TradeStreaks:
    ordered_trades = sort_trades_by_close_time(trades)

    current_wins = 0
    current_losses = 0
    max_wins = 0
    max_losses = 0

    for trade in ordered_trades:
        pnl = trade.net_profit

        if pnl > 0:
            current_wins += 1
            current_losses = 0
        elif pnl < 0:
            current_losses += 1
            current_wins = 0
        else:
            current_wins = 0
            current_losses = 0

        max_wins = max(max_wins, current_wins)
        max_losses = max(max_losses, current_losses)

    return TradeStreaks(
        max_consecutive_wins=max_wins,
        max_consecutive_losses=max_losses,
    )
