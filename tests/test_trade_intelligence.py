from datetime import datetime

import pytest

from analytics.trade_intelligence import calculate_trade_intelligence
from analytics.trade_schema import NormalizedTrade


def _make_trade(ticket: int, closed_at: datetime, net_profit: float, symbol: str) -> NormalizedTrade:
    return NormalizedTrade(
        ticket=ticket,
        opened_at=datetime(2026, 3, 1, 9, 0, 0),
        closed_at=closed_at,
        side="buy",
        size_lots=0.01,
        symbol=symbol,
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


def test_calculate_trade_intelligence_returns_day_hour_and_symbol_patterns() -> None:
    trades = [
        _make_trade(1, datetime(2026, 3, 2, 9, 0, 0), 10.0, "EURUSD"),
        _make_trade(2, datetime(2026, 3, 2, 9, 30, 0), 8.0, "EURUSD"),
        _make_trade(3, datetime(2026, 3, 3, 14, 0, 0), -5.0, "GBPUSD"),
        _make_trade(4, datetime(2026, 3, 3, 14, 30, 0), -7.0, "GBPUSD"),
        _make_trade(5, datetime(2026, 3, 4, 11, 0, 0), 0.0, "USDJPY"),
    ]

    intelligence = calculate_trade_intelligence(trades)

    assert intelligence.best_day_of_week == "Monday"
    assert intelligence.worst_day_of_week == "Tuesday"
    assert intelligence.best_trading_hour == 9
    assert intelligence.worst_trading_hour == 14
    assert intelligence.best_symbol == "EURUSD"
    assert intelligence.worst_symbol == "GBPUSD"
    assert intelligence.win_rate_by_day["Monday"] == pytest.approx(100.0)
    assert intelligence.win_rate_by_day["Tuesday"] == pytest.approx(0.0)
    assert intelligence.win_rate_by_day["Wednesday"] == pytest.approx(0.0)


def test_calculate_trade_intelligence_returns_empty_safe_defaults() -> None:
    intelligence = calculate_trade_intelligence([])

    assert intelligence.best_day_of_week is None
    assert intelligence.worst_day_of_week is None
    assert intelligence.best_trading_hour is None
    assert intelligence.worst_trading_hour is None
    assert intelligence.win_rate_by_day == {}
    assert intelligence.best_symbol is None
    assert intelligence.worst_symbol is None
