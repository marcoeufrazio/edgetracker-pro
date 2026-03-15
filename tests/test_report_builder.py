from pathlib import Path

from analytics.report_builder import build_report_bundle


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_build_report_bundle_returns_metrics_trades_and_health_sections() -> None:
    bundle = build_report_bundle(SAMPLE_STATEMENT_PATH)

    assert bundle.metrics_summary["total_trades"] == 247
    assert bundle.health_score.health_classification
    assert bundle.health_diagnostic
    assert bundle.trade_intelligence.best_day_of_week is not None
    assert bundle.strategy_analyzer.average_trade_duration_minutes > 0
    assert bundle.trades_export_rows
