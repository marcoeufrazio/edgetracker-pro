from __future__ import annotations

from analytics.strategy_analyzer import StrategyAnalyzerResult
from analytics.trade_intelligence import TradeIntelligence


def format_trade_intelligence(intelligence: TradeIntelligence) -> dict[str, str]:
    return {
        "best_day": _format_optional(intelligence.best_day_of_week),
        "worst_day": _format_optional(intelligence.worst_day_of_week),
        "best_hour": _format_hour(intelligence.best_trading_hour),
        "worst_hour": _format_hour(intelligence.worst_trading_hour),
        "best_symbol": _format_optional(intelligence.best_symbol),
        "worst_symbol": _format_optional(intelligence.worst_symbol),
    }


def format_strategy_analyzer(result: StrategyAnalyzerResult) -> dict[str, str]:
    return {
        "average_trade_duration": f"{result.average_trade_duration_minutes:.2f} minutes",
        "best_duration_bucket": _format_best_worst(result.performance_by_duration, "best"),
        "worst_duration_bucket": _format_best_worst(result.performance_by_duration, "worst"),
        "best_size_bucket": _format_best_worst(result.performance_by_position_size, "best"),
        "worst_size_bucket": _format_best_worst(result.performance_by_position_size, "worst"),
        "best_win_streak": _format_best_worst(result.performance_after_win_streak, "best", "wins"),
        "worst_win_streak": _format_best_worst(result.performance_after_win_streak, "worst", "wins"),
        "best_loss_recovery": _format_best_worst(result.performance_after_loss_streak, "best", "losses"),
        "worst_loss_continuation": _format_best_worst(result.performance_after_loss_streak, "worst", "losses"),
    }


def _format_optional(value: object | None) -> str:
    return "Not available" if value is None else str(value)


def _format_hour(value: int | None) -> str:
    if value is None:
        return "Not available"
    return f"{value:02d}:00"


def _format_best_worst(values: dict[object, float], mode: str, suffix: str = "") -> str:
    if not values:
        return "Not available"

    key = max(values, key=values.get) if mode == "best" else min(values, key=values.get)
    label = f"{key} {suffix}".strip()
    return f"{label} ({values[key]:.4f})"
