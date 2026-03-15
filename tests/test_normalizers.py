from pathlib import Path

import pytest

from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trade, normalize_mt4_trades
from analytics.trade_schema import ImportedTradeRow


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_normalize_mt4_trade_converts_raw_values_to_typed_schema() -> None:
    raw_trade = ImportedTradeRow(
        ticket="29356320",
        open_time="2026.02.25 02:50:02",
        trade_type="sell",
        size="0.01",
        item="usdjpy-std",
        open_price="155.730",
        stop_loss="0.000",
        take_profit="0.000",
        close_time="2026.02.25 02:57:23",
        close_price="155.724",
        commission="0.00",
        taxes="0.00",
        swap="0.00",
        profit="0.04",
    )

    trade = normalize_mt4_trade(raw_trade)

    assert trade.ticket == 29356320
    assert trade.side == "sell"
    assert trade.size_lots == 0.01
    assert trade.symbol == "USDJPY"
    assert trade.stop_loss is None
    assert trade.take_profit is None
    assert trade.net_profit == pytest.approx(0.04)
    assert trade.source == "mt4_html"
    assert trade.source_type == "sell"


def test_normalize_mt4_trades_normalizes_sample_statement() -> None:
    imported_trades = import_mt4_closed_trades(SAMPLE_STATEMENT_PATH)

    normalized_trades = normalize_mt4_trades(imported_trades)

    assert normalized_trades
    assert normalized_trades[0].symbol == "USDJPY"
    assert normalized_trades[0].profit == pytest.approx(0.04)
    assert normalized_trades[0].opened_at < normalized_trades[0].closed_at
    assert all(trade.side in {"buy", "sell"} for trade in normalized_trades)
    assert all(trade.net_profit == pytest.approx(trade.commission + trade.taxes + trade.swap + trade.profit) for trade in normalized_trades)
