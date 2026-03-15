from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.strategy_analyzer import analyze_strategy_patterns


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    result = analyze_strategy_patterns(normalized_trades)

    print("EdgeTracker-Pro Module 9 Strategy Analyzer")
    print(f"Average Trade Duration: {result.average_trade_duration_minutes:.2f} minutes")
    print("Duration Performance")
    print(f"  Best duration bucket: {_format_best_worst(result.performance_by_duration, 'best')}")
    print(f"  Worst duration bucket: {_format_best_worst(result.performance_by_duration, 'worst')}")
    print("Position Size Performance")
    print(f"  Best size bucket: {_format_best_worst(result.performance_by_position_size, 'best')}")
    print(f"  Worst size bucket: {_format_best_worst(result.performance_by_position_size, 'worst')}")
    print("Performance After Win Streak")
    print(f"  Best continuation streak: {_format_best_worst(result.performance_after_win_streak, 'best', 'wins')}")
    print(f"  Worst continuation streak: {_format_best_worst(result.performance_after_win_streak, 'worst', 'wins')}")
    print("Performance After Loss Streak")
    print(f"  Best recovery streak: {_format_best_worst(result.performance_after_loss_streak, 'best', 'losses')}")
    print(f"  Worst continuation streak: {_format_best_worst(result.performance_after_loss_streak, 'worst', 'losses')}")
    print("R:R Analysis")
    print(f"  {_format_rr_analysis(result.performance_by_rr)}")


def _format_best_worst(
    values: dict[object, float],
    mode: str,
    suffix: str = "",
) -> str:
    if not values:
        return "Not available"

    key = max(values, key=values.get) if mode == "best" else min(values, key=values.get)
    label = f"{key} {suffix}".strip()
    return f"{label} ({values[key]:.4f})"


def _format_rr_analysis(values: dict[str, float] | None) -> str:
    if not values:
        return "Not available"

    best_key = max(values, key=values.get)
    worst_key = min(values, key=values.get)
    return f"Best={best_key} ({values[best_key]:.4f}), Worst={worst_key} ({values[worst_key]:.4f})"


if __name__ == "__main__":
    main()
