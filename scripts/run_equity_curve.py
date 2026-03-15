from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.equity_builder import build_equity_timeline_from_mt4_statement


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    timeline = build_equity_timeline_from_mt4_statement(
        path=statement_path,
        initial_balance=1000.0,
    )

    print("EdgeTracker-Pro Module 4 Equity Curve")
    print(f"Points: {len(timeline)}")

    for point in timeline[:5]:
        print(
            {
                "trade_number": point.trade_number,
                "close_time": point.close_time.isoformat(sep=" "),
                "pnl": round(point.pnl, 2),
                "cumulative_pnl": round(point.cumulative_pnl, 2),
                "equity": round(point.equity, 2),
            }
        )


if __name__ == "__main__":
    main()
