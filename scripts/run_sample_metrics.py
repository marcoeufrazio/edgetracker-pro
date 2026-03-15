from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.service import calculate_account_metrics


def main() -> None:
    metrics = calculate_account_metrics(
        initial_balance=1_000.0,
        pnl_values=[120.0, -40.0, 85.0, -25.0, 60.0],
        cycle_target=150.0,
    )

    print("EdgeTracker-Pro Module 1 Sample")
    print(f"Equity: {metrics.equity}")
    print(f"Drawdown Abs: {metrics.drawdown_abs_series}")
    print(f"Drawdown Pct: {metrics.drawdown_pct_series}")
    print(f"Max Drawdown Abs: {metrics.max_drawdown_abs:.2f}")
    print(f"Max Drawdown Pct: {metrics.max_drawdown_pct:.2f}")
    print(f"Ulcer Index: {metrics.ulcer_index:.4f}")
    print(f"MAR Ratio: {metrics.mar_ratio:.4f}")
    print(f"Green Target: {metrics.green_target:.2f}")
    print(f"Traffic Light: {metrics.traffic_light}")
    print(f"Health Summary: {metrics.health_summary}")


if __name__ == "__main__":
    main()
