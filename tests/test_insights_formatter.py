from analytics.strategy_analyzer import StrategyAnalyzerResult
from analytics.trade_intelligence import TradeIntelligence
from dashboard.insights_formatter import format_strategy_analyzer, format_trade_intelligence


def test_format_trade_intelligence_returns_readable_strings() -> None:
    intelligence = TradeIntelligence(
        best_day_of_week="Friday",
        worst_day_of_week="Tuesday",
        best_trading_hour=15,
        worst_trading_hour=10,
        win_rate_by_day={"Friday": 100.0},
        best_symbol="USDJPY",
        worst_symbol="EURUSD",
    )

    formatted = format_trade_intelligence(intelligence)

    assert formatted["best_day"] == "Friday"
    assert formatted["worst_day"] == "Tuesday"
    assert formatted["best_hour"] == "15:00"
    assert formatted["worst_hour"] == "10:00"
    assert formatted["best_symbol"] == "USDJPY"
    assert formatted["worst_symbol"] == "EURUSD"


def test_format_strategy_analyzer_returns_readable_strings() -> None:
    result = StrategyAnalyzerResult(
        average_trade_duration_minutes=42.39,
        performance_by_duration={"short": 0.08, "long": -0.69, "medium": 0.10},
        performance_by_position_size={0.01: -0.02, 0.02: 0.03},
        performance_after_win_streak={1: -1.71, 2: 1.99},
        performance_after_loss_streak={1: -2.43, 2: 2.70},
        performance_by_rr=None,
    )

    formatted = format_strategy_analyzer(result)

    assert formatted["average_trade_duration"] == "42.39 minutes"
    assert formatted["best_duration_bucket"] == "medium (0.1000)"
    assert formatted["worst_duration_bucket"] == "long (-0.6900)"
    assert formatted["best_size_bucket"] == "0.02 (0.0300)"
    assert formatted["worst_size_bucket"] == "0.01 (-0.0200)"
    assert formatted["best_win_streak"] == "2 wins (1.9900)"
    assert formatted["worst_win_streak"] == "1 wins (-1.7100)"
    assert formatted["best_loss_recovery"] == "2 losses (2.7000)"
    assert formatted["worst_loss_continuation"] == "1 losses (-2.4300)"
