from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analytics.exporters import export_csv, export_markdown
from analytics.report_builder import build_report_bundle
from analytics.report_formatter import format_report_summary_markdown


def main() -> None:
    statement_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    output_dir = PROJECT_ROOT / "outputs" / "reports"

    bundle = build_report_bundle(statement_path)
    metrics_rows = [bundle.metrics_summary]
    markdown_report = format_report_summary_markdown(bundle)

    metrics_path = export_csv(metrics_rows, output_dir / "metrics_summary.csv")
    trades_path = export_csv(bundle.trades_export_rows, output_dir / "trades_export.csv")
    report_path = export_markdown(markdown_report, output_dir / "report_summary.md")

    print("EdgeTracker-Pro Module 13 Reports Export")
    print(f"Metrics summary: {metrics_path}")
    print(f"Trades export: {trades_path}")
    print(f"Markdown report: {report_path}")


if __name__ == "__main__":
    main()
