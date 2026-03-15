from datetime import datetime

from analytics.trade_schema import NormalizedTrade
from dashboard.trade_table import build_trade_table_rows


def _make_trade(ticket: int, stop_loss: float | None = None) -> NormalizedTrade:
    return NormalizedTrade(
        ticket=ticket,
        opened_at=datetime(2026, 3, 1, 9, 0, 0),
        closed_at=datetime(2026, 3, 1, 10, 15, 0),
        side="buy",
        size_lots=0.02,
        symbol="EURUSD",
        open_price=100.0,
        stop_loss=stop_loss,
        take_profit=None,
        close_price=104.0,
        commission=0.0,
        taxes=0.0,
        swap=0.0,
        profit=4.0,
        net_profit=4.0,
        source="mt4_html",
        source_type="buy",
    )


def test_build_trade_table_rows_returns_core_fields_and_optional_fields() -> None:
    rows = build_trade_table_rows([_make_trade(1, stop_loss=98.0), _make_trade(2, stop_loss=None)])

    assert rows[0]["ticket"] == 1
    assert rows[0]["symbol"] == "EURUSD"
    assert rows[0]["type"] == "buy"
    assert rows[0]["volume"] == 0.02
    assert rows[0]["duration_minutes"] == 75.0
    assert "r_multiple" in rows[0]
    assert "r_multiple" not in rows[1]
