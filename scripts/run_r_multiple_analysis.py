from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.r_multiple import calculate_r_multiple_summary


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    trade_results, summary = calculate_r_multiple_summary(normalized_trades)

    print("EdgeTracker-Pro Module 9.1 R-Multiple Analysis")
    print(f"Total Trades: {summary.total_trades}")
    print(f"Trades With R: {summary.trades_with_r}")
    print(f"Trades Without R: {summary.trades_without_r}")
    print(f"Average R-Multiple: {summary.average_r_multiple:.4f}")
    print(f"Best R-Multiple: {summary.best_r_multiple:.4f}")
    print(f"Worst R-Multiple: {summary.worst_r_multiple:.4f}")

    if trade_results:
        first_result = trade_results[0]
        print(
            "Sample Eligible Trade:",
            {
                "ticket": first_result.ticket,
                "initial_risk": round(first_result.initial_risk, 6),
                "realized_reward": round(first_result.realized_reward, 6),
                "r_multiple": round(first_result.r_multiple, 4),
            },
        )


if __name__ == "__main__":
    main()
