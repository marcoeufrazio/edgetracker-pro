from datetime import datetime

import pytest

from analytics.r_multiple_synthetic import calculate_synthetic_r_multiple
from analytics.trade_schema import NormalizedTrade


def _make_trade(ticket: int, net_profit: float) -> NormalizedTrade:
    return NormalizedTrade(
        ticket=ticket,
        opened_at=datetime(2026, 3, 1, 9, 0, 0),
        closed_at=datetime(2026, 3, 1, 10, 0, 0),
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


def test_calculate_synthetic_r_multiple_uses_average_loss_as_r_base() -> None:
    trades = [
        _make_trade(1, 20.0),
        _make_trade(2, -10.0),
        _make_trade(3, 5.0),
        _make_trade(4, -20.0),
    ]

    r_values, summary = calculate_synthetic_r_multiple(trades)

    assert summary.average_loss == pytest.approx(15.0)
    assert r_values == pytest.approx([1.3333333333, -0.6666666667, 0.3333333333, -1.3333333333])
    assert summary.average_r == pytest.approx(-0.0833333333)
    assert summary.best_r == pytest.approx(1.3333333333)
    assert summary.worst_r == pytest.approx(-1.3333333333)
    assert summary.distribution_r["0R to 1R"] == 1
    assert summary.distribution_r["1R to 2R"] == 1
    assert summary.distribution_r["-1R to 0R"] == 1
    assert summary.distribution_r["-2R to -1R"] == 1


def test_calculate_synthetic_r_multiple_returns_empty_when_average_loss_is_zero() -> None:
    trades = [_make_trade(1, 10.0), _make_trade(2, 5.0)]

    r_values, summary = calculate_synthetic_r_multiple(trades)

    assert r_values == []
    assert summary.average_loss == 0.0
    assert summary.average_r == 0.0
    assert summary.distribution_r == {}
