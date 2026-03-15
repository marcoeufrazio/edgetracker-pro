from datetime import date, datetime

from analytics.trade_schema import NormalizedTrade
from dashboard.filters import TradeFilters, apply_trade_filters, get_filter_options


def _make_trade(ticket: int, symbol: str, closed_at: datetime, net_profit: float) -> NormalizedTrade:
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


def test_apply_trade_filters_filters_by_symbol_result_day_hour_and_date() -> None:
    trades = [
        _make_trade(1, "EURUSD", datetime(2026, 3, 2, 10, 0, 0), 10.0),
        _make_trade(2, "GBPUSD", datetime(2026, 3, 3, 11, 0, 0), -5.0),
        _make_trade(3, "EURUSD", datetime(2026, 3, 2, 10, 30, 0), 15.0),
    ]

    filters = TradeFilters(
        symbol="EURUSD",
        result_type="wins",
        day_of_week="Monday",
        hour_of_day=10,
        date_from=date(2026, 3, 2),
        date_to=date(2026, 3, 2),
    )

    result = apply_trade_filters(trades, filters)

    assert [trade.ticket for trade in result] == [1, 3]


def test_get_filter_options_returns_sorted_choices() -> None:
    trades = [
        _make_trade(1, "GBPUSD", datetime(2026, 3, 3, 11, 0, 0), -5.0),
        _make_trade(2, "EURUSD", datetime(2026, 3, 2, 10, 0, 0), 10.0),
    ]

    options = get_filter_options(trades)

    assert options["symbols"] == ["all", "EURUSD", "GBPUSD"]
    assert options["result_types"] == ["all", "wins", "losses"]
    assert options["hours_of_day"] == ["all", 10, 11]
