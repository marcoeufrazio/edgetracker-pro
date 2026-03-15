from datetime import datetime

from analytics.streaks import calculate_trade_streaks
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


def test_calculate_trade_streaks_returns_max_winning_and_losing_runs() -> None:
    trades = [
        _make_trade(1, datetime(2026, 3, 1, 10, 0, 0), 10.0),
        _make_trade(2, datetime(2026, 3, 1, 11, 0, 0), 12.0),
        _make_trade(3, datetime(2026, 3, 1, 12, 0, 0), -5.0),
        _make_trade(4, datetime(2026, 3, 1, 13, 0, 0), -7.0),
        _make_trade(5, datetime(2026, 3, 1, 14, 0, 0), -3.0),
        _make_trade(6, datetime(2026, 3, 1, 15, 0, 0), 8.0),
    ]

    streaks = calculate_trade_streaks(trades)

    assert streaks.max_consecutive_wins == 2
    assert streaks.max_consecutive_losses == 3


def test_calculate_trade_streaks_breaks_on_breakeven_trades() -> None:
    trades = [
        _make_trade(1, datetime(2026, 3, 1, 10, 0, 0), 10.0),
        _make_trade(2, datetime(2026, 3, 1, 11, 0, 0), 0.0),
        _make_trade(3, datetime(2026, 3, 1, 12, 0, 0), 5.0),
    ]

    streaks = calculate_trade_streaks(trades)

    assert streaks.max_consecutive_wins == 1
    assert streaks.max_consecutive_losses == 0
