from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.account_comparison import build_account_comparison
from analytics.multi_account import analyze_multiple_accounts


def main() -> None:
    statement_paths = sorted((PROJECT_ROOT / "data" / "imports").glob("mt4_statement.ht*"))
    analyses = analyze_multiple_accounts(statement_paths)
    comparison = build_account_comparison(analyses)

    print("EdgeTracker-Pro Module 14 Multi Account Analysis")
    print("Comparison Table:")
    for row in comparison.comparison_table:
        print(row)

    print("Aggregated Metrics:")
    print(comparison.aggregated_metrics)

    print("Performance Ranking:")
    for row in comparison.performance_ranking:
        print(row)


if __name__ == "__main__":
    main()
