from pathlib import Path

import pytest

from analytics.equity_builder import build_equity_timeline_from_mt4_statement, build_equity_timeline_from_trades
from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_build_equity_timeline_from_trades_uses_existing_normalized_trades() -> None:
    imported_trades = import_mt4_closed_trades(SAMPLE_STATEMENT_PATH)
    normalized_trades = normalize_mt4_trades(imported_trades)

    timeline = build_equity_timeline_from_trades(normalized_trades, initial_balance=1000.0)

    assert timeline
    assert timeline[0].trade_number == 1
    assert timeline[-1].trade_number == len(normalized_trades)
    assert timeline[-1].equity == pytest.approx(994.49)


def test_build_equity_timeline_from_mt4_statement_reads_sample_html() -> None:
    timeline = build_equity_timeline_from_mt4_statement(SAMPLE_STATEMENT_PATH, initial_balance=1000.0)

    assert timeline
    assert timeline[0].close_time <= timeline[-1].close_time
    assert timeline[-1].cumulative_pnl == pytest.approx(-5.51)
