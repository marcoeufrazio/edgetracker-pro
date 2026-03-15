from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.chart_export import export_chart
from analytics.charts import create_drawdown_curve_chart, create_equity_curve_chart
from analytics.drawdown_series import build_drawdown_series_from_mt4_statement
from analytics.equity_builder import build_equity_timeline_from_mt4_statement


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    output_dir = PROJECT_ROOT / "outputs" / "charts"

    timeline = build_equity_timeline_from_mt4_statement(
        path=statement_path,
        initial_balance=1000.0,
    )
    drawdown_series = build_drawdown_series_from_mt4_statement(
        path=statement_path,
        initial_balance=1000.0,
    )

    equity_chart = create_equity_curve_chart(timeline)
    drawdown_chart = create_drawdown_curve_chart(drawdown_series)

    equity_path = export_chart(equity_chart, output_dir / "equity_curve.png")
    drawdown_path = export_chart(drawdown_chart, output_dir / "drawdown_curve.png")

    print("EdgeTracker-Pro Module 5.1 Charts")
    print(f"Equity chart: {equity_path}")
    print(f"Drawdown chart: {drawdown_path}")


if __name__ == "__main__":
    main()
