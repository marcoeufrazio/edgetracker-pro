from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.performance import calculate_performance_metrics
from analytics.streaks import calculate_trade_streaks


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)

    performance = calculate_performance_metrics(normalized_trades)
    streaks = calculate_trade_streaks(normalized_trades)

    print("EdgeTracker-Pro Module 5.2 Performance Analytics")
    print(f"Total Trades: {performance.total_trades}")
    print(f"Winning Trades: {performance.winning_trades}")
    print(f"Losing Trades: {performance.losing_trades}")
    print(f"Breakeven Trades: {performance.breakeven_trades}")
    print(f"Win Rate: {performance.win_rate:.2f}%")
    print(f"Gross Profit: {performance.gross_profit:.2f}")
    print(f"Gross Loss: {performance.gross_loss:.2f}")
    print(f"Net Profit: {performance.net_profit:.2f}")
    print(f"Average Win: {performance.average_win:.2f}")
    print(f"Average Loss: {performance.average_loss:.2f}")
    print(f"Profit Factor: {performance.profit_factor:.4f}")
    print(f"Expectancy: {performance.expectancy:.4f}")
    print(f"Max Consecutive Wins: {streaks.max_consecutive_wins}")
    print(f"Max Consecutive Losses: {streaks.max_consecutive_losses}")


if __name__ == "__main__":
    main()
