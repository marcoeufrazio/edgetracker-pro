from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades


def main() -> None:
    sample_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    imported_trades = import_mt4_closed_trades(sample_path)
    normalized_trades = normalize_mt4_trades(imported_trades)

    print("EdgeTracker-Pro Module 2 Sample")
    print(f"Imported closed trades: {len(imported_trades)}")

    if not normalized_trades:
        print("No normalized trades found.")
        return

    first_trade = normalized_trades[0]
    print(
        "First trade:",
        {
            "ticket": first_trade.ticket,
            "symbol": first_trade.symbol,
            "side": first_trade.side,
            "opened_at": first_trade.opened_at.isoformat(sep=' '),
            "closed_at": first_trade.closed_at.isoformat(sep=' '),
            "net_profit": round(first_trade.net_profit, 2),
        },
    )


if __name__ == "__main__":
    main()
