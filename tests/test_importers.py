from pathlib import Path

import pytest

from analytics.importers import import_mt4_closed_trades, parse_mt4_statement_rows, resolve_mt4_statement_path


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_resolve_mt4_statement_path_supports_html_alias_for_existing_sample() -> None:
    resolved_path = resolve_mt4_statement_path(SAMPLE_STATEMENT_PATH)

    assert resolved_path.name == "mt4_statement.htm"


def test_parse_mt4_statement_rows_reads_table_rows_from_sample() -> None:
    rows = parse_mt4_statement_rows(SAMPLE_STATEMENT_PATH)

    assert any(row[0] == "Closed Transactions:" for row in rows if row)
    assert any(row[0] == "Open Trades:" for row in rows if row)


def test_import_mt4_closed_trades_extracts_only_closed_buy_sell_rows() -> None:
    trades = import_mt4_closed_trades(SAMPLE_STATEMENT_PATH)

    assert trades
    assert all(trade.trade_type in {"buy", "sell"} for trade in trades)
    assert all(trade.item for trade in trades)
    assert trades[0].ticket == "29356320"
    assert trades[0].profit == "0.04"


def test_import_mt4_closed_trades_raises_when_section_is_missing(tmp_path: Path) -> None:
    invalid_statement = tmp_path / "invalid_statement.html"
    invalid_statement.write_text("<html><body><table><tr><td>Ticket</td></tr></table></body></html>", encoding="utf-8")

    with pytest.raises(ValueError, match="Closed Transactions section not found"):
        import_mt4_closed_trades(invalid_statement)
