from datetime import datetime

import pytest

from analytics.r_multiple import calculate_r_multiple_summary
from analytics.trade_schema import NormalizedTrade


def _make_trade(
    *,
    ticket: int,
    side: str,
    open_price: float,
    close_price: float,
    stop_loss: float | None,
    size_lots: float = 1.0,
) -> NormalizedTrade:
    return NormalizedTrade(
        ticket=ticket,
        opened_at=datetime(2026, 3, 1, 9, 0, 0),
        closed_at=datetime(2026, 3, 1, 10, 0, 0),
        side=side,
        size_lots=size_lots,
        symbol="EURUSD",
        open_price=open_price,
        stop_loss=stop_loss,
        take_profit=None,
        close_price=close_price,
        commission=0.0,
        taxes=0.0,
        swap=0.0,
        profit=0.0,
        net_profit=0.0,
        source="mt4_html",
        source_type=side,
    )


def test_calculate_r_multiple_summary_returns_aggregate_metrics() -> None:
    trades = [
        _make_trade(ticket=1, side="buy", open_price=100.0, close_price=104.0, stop_loss=98.0),
        _make_trade(ticket=2, side="sell", open_price=100.0, close_price=99.0, stop_loss=101.0),
        _make_trade(ticket=3, side="buy", open_price=100.0, close_price=102.0, stop_loss=None),
    ]

    trade_results, summary = calculate_r_multiple_summary(trades)

    assert len(trade_results) == 2
    assert summary.total_trades == 3
    assert summary.trades_with_r == 2
    assert summary.trades_without_r == 1
    assert summary.average_r_multiple == pytest.approx(1.5)
    assert summary.best_r_multiple == pytest.approx(2.0)
    assert summary.worst_r_multiple == pytest.approx(1.0)


def test_calculate_r_multiple_summary_returns_zero_summary_for_empty_input() -> None:
    trade_results, summary = calculate_r_multiple_summary([])

    assert trade_results == []
    assert summary.total_trades == 0
    assert summary.trades_with_r == 0
    assert summary.trades_without_r == 0
    assert summary.average_r_multiple == 0.0
