from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.drawdown_series import build_drawdown_series_from_mt4_statement


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    series = build_drawdown_series_from_mt4_statement(
        path=statement_path,
        initial_balance=1000.0,
    )

    print("EdgeTracker-Pro Module 4.1 Drawdown Series")
    print(f"Points: {len(series)}")

    for point in series[:5]:
        print(
            {
                "trade_number": point.trade_number,
                "close_time": point.close_time.isoformat(sep=" "),
                "equity": round(point.equity, 2),
                "peak_equity": round(point.peak_equity, 2),
                "drawdown_abs": round(point.drawdown_abs, 2),
                "drawdown_pct": round(point.drawdown_pct, 2),
                "risk_zone": point.risk_zone,
            }
        )


if __name__ == "__main__":
    main()
