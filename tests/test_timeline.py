from datetime import datetime

import pytest

from analytics.timeline import build_trade_timeline, sort_trades_by_close_time
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


def test_sort_trades_by_close_time_orders_by_close_time_then_ticket() -> None:
    trades = [
        _make_trade(3, datetime(2026, 3, 1, 10, 5, 0), 5.0),
        _make_trade(1, datetime(2026, 3, 1, 10, 0, 0), 2.0),
        _make_trade(2, datetime(2026, 3, 1, 10, 0, 0), -1.0),
    ]

    ordered_trades = sort_trades_by_close_time(trades)

    assert [trade.ticket for trade in ordered_trades] == [1, 2, 3]


def test_build_trade_timeline_creates_cumulative_pnl_and_equity_series() -> None:
    trades = [
        _make_trade(2, datetime(2026, 3, 1, 10, 10, 0), -10.0),
        _make_trade(1, datetime(2026, 3, 1, 10, 0, 0), 25.0),
    ]

    timeline = build_trade_timeline(trades=trades, initial_balance=1000.0)

    assert [point.trade_number for point in timeline] == [1, 2]
    assert [point.pnl for point in timeline] == [25.0, -10.0]
    assert [point.cumulative_pnl for point in timeline] == pytest.approx([25.0, 15.0])
    assert [point.equity for point in timeline] == pytest.approx([1025.0, 1015.0])
