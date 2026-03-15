from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.trade_intelligence import calculate_trade_intelligence


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    intelligence = calculate_trade_intelligence(normalized_trades)

    print("EdgeTracker-Pro Module 8 Trade Intelligence")
    print(f"Best Day Of Week: {intelligence.best_day_of_week}")
    print(f"Worst Day Of Week: {intelligence.worst_day_of_week}")
    print(f"Best Trading Hour: {intelligence.best_trading_hour}")
    print(f"Worst Trading Hour: {intelligence.worst_trading_hour}")
    print(f"Best Symbol: {intelligence.best_symbol}")
    print(f"Worst Symbol: {intelligence.worst_symbol}")
    print("Win Rate By Day:")
    for day, win_rate in intelligence.win_rate_by_day.items():
        print(f"  {day}: {win_rate:.2f}%")


if __name__ == "__main__":
    main()
