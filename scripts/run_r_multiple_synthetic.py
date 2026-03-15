from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.r_multiple_synthetic import calculate_synthetic_r_multiple


MAX_BAR_WIDTH = 24


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    r_values, summary = calculate_synthetic_r_multiple(normalized_trades)

    print("EdgeTracker-Pro Module 9.2 Synthetic R Analysis")
    print(f"Average Loss: {summary.average_loss:.4f}")
    print(f"Average R: {summary.average_r:.4f}")
    print(f"Best R: {summary.best_r:.4f}")
    print(f"Worst R: {summary.worst_r:.4f}")
    print()
    print("R Distribution")
    _print_r_distribution(summary.distribution_r)

    if r_values:
        print(f"Sample R Values: {[round(value, 4) for value in r_values[:5]]}")


def _print_r_distribution(distribution: dict[str, int]) -> None:
    if not distribution:
        print("Not available")
        return

    total = sum(distribution.values())
    largest_bucket = max(distribution.values(), default=0)

    for label, count in distribution.items():
        percentage = (count / total) * 100 if total else 0.0
        bar = _build_bar(count, largest_bucket)
        print(f"{_format_bucket_label(label):<12} | {count:>3} | {percentage:>6.2f}% | {bar}")


def _build_bar(count: int, largest_bucket: int) -> str:
    if count <= 0 or largest_bucket <= 0:
        return ""

    bar_width = max(1, round((count / largest_bucket) * MAX_BAR_WIDTH))
    return "#" * bar_width


def _format_bucket_label(label: str) -> str:
    return {
        "<=-2R": "<= -2R",
        ">=2R": ">= 2R",
    }.get(label, label)


if __name__ == "__main__":
    main()
