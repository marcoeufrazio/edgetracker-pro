from datetime import datetime

import pytest

from analytics.strategy_analyzer import analyze_strategy_patterns
from analytics.trade_schema import NormalizedTrade


def _make_trade(
    ticket: int,
    opened_at: datetime,
    closed_at: datetime,
    net_profit: float,
    size_lots: float = 0.01,
) -> NormalizedTrade:
    return NormalizedTrade(
        ticket=ticket,
        opened_at=opened_at,
        closed_at=closed_at,
        side="buy",
        size_lots=size_lots,
        symbol="EURUSD",
        open_price=1.1,
        stop_loss=None,
        take_profit=None,
        close_price=1.1005,
        commission=0.0,
        taxes=0.0,
        swap=0.0,
        profit=net_profit,
        net_profit=net_profit,
        source="mt4_html",
        source_type="buy",
    )


def test_analyze_strategy_patterns_returns_grouped_metrics() -> None:
    trades = [
        _make_trade(1, datetime(2026, 3, 1, 10, 0), datetime(2026, 3, 1, 10, 10), 10.0, 0.01),
        _make_trade(2, datetime(2026, 3, 1, 11, 0), datetime(2026, 3, 1, 11, 40), 20.0, 0.02),
        _make_trade(3, datetime(2026, 3, 1, 12, 0), datetime(2026, 3, 1, 14, 0), -15.0, 0.02),
        _make_trade(4, datetime(2026, 3, 1, 15, 0), datetime(2026, 3, 1, 15, 5), 5.0, 0.01),
    ]

    result = analyze_strategy_patterns(trades)

    assert result.average_trade_duration_minutes == pytest.approx(43.75)
    assert result.performance_by_duration["short"] == pytest.approx(7.5)
    assert result.performance_by_duration["medium"] == pytest.approx(20.0)
    assert result.performance_by_duration["long"] == pytest.approx(-15.0)
    assert result.performance_by_position_size[0.01] == pytest.approx(7.5)
    assert result.performance_by_position_size[0.02] == pytest.approx(2.5)
    assert result.performance_after_win_streak[1] == pytest.approx(20.0)
    assert result.performance_after_win_streak[2] == pytest.approx(-15.0)
    assert result.performance_after_loss_streak[1] == pytest.approx(5.0)
    assert result.performance_by_rr is None


def test_analyze_strategy_patterns_returns_empty_safe_defaults() -> None:
    result = analyze_strategy_patterns([])

    assert result.average_trade_duration_minutes == 0.0
    assert result.performance_by_duration == {}
    assert result.performance_by_position_size == {}
    assert result.performance_after_win_streak == {}
    assert result.performance_after_loss_streak == {}
    assert result.performance_by_rr is None
