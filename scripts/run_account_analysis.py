from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.importers import import_mt4_closed_trades, load_mt4_statement_html
from analytics.normalizers import normalize_mt4_trades
from analytics.service import calculate_account_metrics


DEFAULT_CYCLE_TARGET_RATE = 0.05


def main() -> None:
    args = _parse_args()
    statement_path = PROJECT_ROOT / args.statement_path
    statement_html = load_mt4_statement_html(statement_path)

    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    pnl_values = [trade.net_profit for trade in normalized_trades]

    final_balance = _extract_summary_metric(statement_html, "Balance:")
    total_net_profit = _extract_summary_metric(statement_html, "Total Net Profit:")
    initial_balance = final_balance - total_net_profit
    cycle_target = args.cycle_target if args.cycle_target is not None else _derive_cycle_target(initial_balance)

    metrics = calculate_account_metrics(
        initial_balance=initial_balance,
        pnl_values=pnl_values,
        cycle_target=cycle_target,
    )

    print("EdgeTracker-Pro Module 3 Account Analysis")
    print(f"Trades: {len(normalized_trades)}")
    print(f"Equity Final: {metrics.equity[-1]:.2f}")
    print(f"Max Drawdown: {metrics.max_drawdown_abs:.2f} ({metrics.max_drawdown_pct:.2f}%)")
    print(f"Ulcer Index: {metrics.ulcer_index:.4f}")
    print(f"MAR Ratio: {metrics.mar_ratio:.4f}")
    print(f"Traffic Light: {metrics.traffic_light}")
    print(f"Health Summary: {metrics.health_summary}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run EdgeTracker-Pro account analysis from an MT4 HTML statement.")
    parser.add_argument(
        "statement_path",
        nargs="?",
        default=Path("data/imports/mt4_statement.html"),
        type=Path,
        help="Path to the MT4 HTML statement file.",
    )
    parser.add_argument(
        "--cycle-target",
        type=float,
        default=None,
        help="Manual cycle target override. If omitted, the script derives it automatically.",
    )
    return parser.parse_args()


def _derive_cycle_target(initial_balance: float) -> float:
    return round(initial_balance * DEFAULT_CYCLE_TARGET_RATE, 2)


def _extract_summary_metric(html: str, label: str) -> float:
    escaped_label = re.escape(label)
    pattern = rf"<b>{escaped_label}</b></td>\s*<td[^>]*class=mspt><b>([-0-9.,]+)</b>"
    match = re.search(pattern, html)
    if match is None:
        raise ValueError(f"Unable to extract summary metric for label: {label}")

    return float(match.group(1).replace(",", ""))


if __name__ == "__main__":
    main()
