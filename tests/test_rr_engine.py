from datetime import datetime

import pytest

from analytics.rr_engine import calculate_trade_r_metrics
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


def test_calculate_trade_r_metrics_returns_r_multiple_for_valid_buy_trade() -> None:
    trade = _make_trade(ticket=1, side="buy", open_price=100.0, close_price=104.0, stop_loss=98.0)

    result = calculate_trade_r_metrics(trade)

    assert result is not None
    assert result.initial_risk == pytest.approx(2.0)
    assert result.realized_reward == pytest.approx(4.0)
    assert result.r_multiple == pytest.approx(2.0)


def test_calculate_trade_r_metrics_returns_r_multiple_for_valid_sell_trade() -> None:
    trade = _make_trade(ticket=2, side="sell", open_price=100.0, close_price=97.0, stop_loss=101.0)

    result = calculate_trade_r_metrics(trade)

    assert result is not None
    assert result.initial_risk == pytest.approx(1.0)
    assert result.realized_reward == pytest.approx(3.0)
    assert result.r_multiple == pytest.approx(3.0)


def test_calculate_trade_r_metrics_ignores_trade_without_valid_stop_loss() -> None:
    trade = _make_trade(ticket=3, side="buy", open_price=100.0, close_price=103.0, stop_loss=None)

    assert calculate_trade_r_metrics(trade) is None
