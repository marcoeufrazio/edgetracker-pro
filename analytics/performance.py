from __future__ import annotations

from dataclasses import dataclass

from analytics.timeline import sort_trades_by_close_time
from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class PerformanceMetrics:
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    win_rate: float
    gross_profit: float
    gross_loss: float
    net_profit: float
    average_win: float
    average_loss: float
    profit_factor: float
    expectancy: float


def calculate_performance_metrics(trades: list[NormalizedTrade]) -> PerformanceMetrics:
    ordered_trades = sort_trades_by_close_time(trades)
    pnl_values = [trade.net_profit for trade in ordered_trades]

    winning_values = [pnl for pnl in pnl_values if pnl > 0]
    losing_values = [pnl for pnl in pnl_values if pnl < 0]
    breakeven_values = [pnl for pnl in pnl_values if pnl == 0]

    total_trades = len(pnl_values)
    winning_trades = len(winning_values)
    losing_trades = len(losing_values)
    breakeven_trades = len(breakeven_values)

    gross_profit = sum(winning_values)
    gross_loss = abs(sum(losing_values))
    net_profit = sum(pnl_values)
    average_win = gross_profit / winning_trades if winning_trades else 0.0
    average_loss = abs(sum(losing_values) / losing_trades) if losing_trades else 0.0
    win_rate = (winning_trades / total_trades) * 100 if total_trades else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
    expectancy = net_profit / total_trades if total_trades else 0.0

    return PerformanceMetrics(
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        breakeven_trades=breakeven_trades,
        win_rate=win_rate,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        net_profit=net_profit,
        average_win=average_win,
        average_loss=average_loss,
        profit_factor=profit_factor,
        expectancy=expectancy,
    )
