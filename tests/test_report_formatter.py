from analytics.health_score import HealthScoreResult
from analytics.report_builder import ReportBundle
from analytics.report_formatter import format_report_summary_markdown
from analytics.strategy_analyzer import StrategyAnalyzerResult
from analytics.trade_intelligence import TradeIntelligence


def test_format_report_summary_markdown_contains_expected_sections() -> None:
    bundle = ReportBundle(
        generated_at="2026-03-15T12:00:00+00:00",
        metrics_summary={
            "total_trades": 10,
            "win_rate": 60.0,
            "profit_factor": 1.5,
            "expectancy": 0.2,
            "net_profit": 25.0,
            "traffic_light": "green",
            "risk_zone": "yellow",
            "max_drawdown_pct": 6.5,
            "ulcer_index": 3.2,
            "health_score": 72,
            "health_classification": "good",
        },
        trades_export_rows=[{"ticket": 1}],
        trade_intelligence=TradeIntelligence(
            best_day_of_week="Friday",
            worst_day_of_week="Tuesday",
            best_trading_hour=15,
            worst_trading_hour=10,
            win_rate_by_day={"Friday": 100.0},
            best_symbol="USDJPY",
            worst_symbol="EURUSD",
        ),
        strategy_analyzer=StrategyAnalyzerResult(
            average_trade_duration_minutes=42.39,
            performance_by_duration={"medium": 0.1, "long": -0.6},
            performance_by_position_size={0.01: -0.02, 0.02: 0.03},
            performance_after_win_streak={1: -1.2, 2: 1.8},
            performance_after_loss_streak={1: -2.0, 2: 2.4},
            performance_by_rr=None,
        ),
        health_score=HealthScoreResult(72, "good"),
        health_diagnostic="Trading health is good.",
    )

    markdown = format_report_summary_markdown(bundle)

    assert "# EdgeTracker-Pro Report Summary" in markdown
    assert "## Main Metrics" in markdown
    assert "## Health" in markdown
    assert "## Trade Intelligence" in markdown
    assert "## Strategy Analyzer" in markdown
    assert "Trading health is good." in markdown
