from datetime import datetime

import pytest

from analytics.performance import calculate_performance_metrics
from analytics.trade_schema import NormalizedTrade


def _make_trade(ticket: int, closed_at: datetime, net_profit: float) -> NormalizedTrade:
    return NormalizedTrade(
        ticket=ticket,
        opened_at=datetime(2026, 3, 1, 9, 0, 0),
        closed_at=closed_at,
        side="buy",
        size_lots=0.01,
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


def test_calculate_performance_metrics_returns_expected_summary() -> None:
    trades = [
        _make_trade(1, datetime(2026, 3, 1, 10, 0, 0), 20.0),
        _make_trade(2, datetime(2026, 3, 1, 11, 0, 0), -10.0),
        _make_trade(3, datetime(2026, 3, 1, 12, 0, 0), 0.0),
        _make_trade(4, datetime(2026, 3, 1, 13, 0, 0), 30.0),
    ]

    metrics = calculate_performance_metrics(trades)

    assert metrics.total_trades == 4
    assert metrics.winning_trades == 2
    assert metrics.losing_trades == 1
    assert metrics.breakeven_trades == 1
    assert metrics.win_rate == pytest.approx(50.0)
    assert metrics.gross_profit == pytest.approx(50.0)
    assert metrics.gross_loss == pytest.approx(10.0)
    assert metrics.net_profit == pytest.approx(40.0)
    assert metrics.average_win == pytest.approx(25.0)
    assert metrics.average_loss == pytest.approx(10.0)
    assert metrics.profit_factor == pytest.approx(5.0)
    assert metrics.expectancy == pytest.approx(10.0)


def test_calculate_performance_metrics_returns_zero_safely_for_empty_input() -> None:
    metrics = calculate_performance_metrics([])

    assert metrics.total_trades == 0
    assert metrics.win_rate == 0.0
    assert metrics.profit_factor == 0.0
    assert metrics.expectancy == 0.0
