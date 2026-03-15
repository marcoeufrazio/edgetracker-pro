from datetime import date, datetime

from analytics.trade_schema import NormalizedTrade
from dashboard.filters import TradeFilters
from dashboard.trade_explorer import build_filtered_trade_rows


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


def test_build_filtered_trade_rows_applies_filters_before_building_rows() -> None:
    trades = [
        _make_trade(1, "EURUSD", datetime(2026, 3, 2, 10, 0, 0), 10.0),
        _make_trade(2, "GBPUSD", datetime(2026, 3, 3, 11, 0, 0), -5.0),
    ]
    filters = TradeFilters(symbol="EURUSD", result_type="wins", date_from=date(2026, 3, 2), date_to=date(2026, 3, 2))

    rows = build_filtered_trade_rows(trades, filters)

    assert len(rows) == 1
    assert rows[0]["ticket"] == 1
