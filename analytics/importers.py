from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from analytics.trade_schema import ESSENTIAL_TRADE_FIELDS, ImportedTradeRow, MT4_CLOSED_TRADES_HEADERS


class _TableRowParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None
        self._cell_colspan = 1
        self._in_cell = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if tag == "tr":
            self._current_row = []
            return

        if tag != "td" or self._current_row is None:
            return

        self._in_cell = True
        self._current_cell = []
        colspan = attrs_dict.get("colspan", "1") or "1"
        self._cell_colspan = int(colspan)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._current_row is not None and self._current_cell is not None:
            value = " ".join("".join(self._current_cell).split())
            self._current_row.append(value)

            for _ in range(self._cell_colspan - 1):
                self._current_row.append("")

            self._current_cell = None
            self._cell_colspan = 1
            self._in_cell = False
            return

        if tag == "tr" and self._current_row is not None:
            if any(cell.strip() for cell in self._current_row):
                self.rows.append(self._current_row)
            self._current_row = None

    def handle_data(self, data: str) -> None:
        if self._in_cell and self._current_cell is not None:
            self._current_cell.append(data)


def resolve_mt4_statement_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.exists():
        return candidate

    alternate_extensions = {".html": ".htm", ".htm": ".html"}
    alternate_suffix = alternate_extensions.get(candidate.suffix.lower())
    if alternate_suffix is None:
        raise FileNotFoundError(f"MT4 statement file not found: {candidate}")

    alternate = candidate.with_suffix(alternate_suffix)
    if alternate.exists():
        return alternate

    raise FileNotFoundError(f"MT4 statement file not found: {candidate}")


def load_mt4_statement_html(path: str | Path) -> str:
    statement_path = resolve_mt4_statement_path(path)

    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return statement_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return statement_path.read_text(encoding="utf-8", errors="replace")


def parse_mt4_statement_rows(path: str | Path) -> list[list[str]]:
    parser = _TableRowParser()
    parser.feed(load_mt4_statement_html(path))
    return parser.rows


def import_mt4_closed_trades(path: str | Path) -> list[ImportedTradeRow]:
    rows = parse_mt4_statement_rows(path)

    header_index = _find_closed_trades_header_index(rows)
    header_row = rows[header_index]
    _validate_mt4_header(header_row)

    imported_rows: list[ImportedTradeRow] = []
    for row in rows[header_index + 1 :]:
        if _is_section_marker(row, "Open Trades:"):
            break

        if len(row) != len(MT4_CLOSED_TRADES_HEADERS):
            continue

        row_data = dict(zip(MT4_CLOSED_TRADES_HEADERS, row))
        trade_type = row_data["type"].strip().lower()
        if trade_type not in {"buy", "sell"}:
            continue

        imported_rows.append(
            ImportedTradeRow(
                ticket=row_data["ticket"],
                open_time=row_data["open_time"],
                trade_type=row_data["type"],
                size=row_data["size"],
                item=row_data["item"],
                open_price=row_data["open_price"],
                stop_loss=row_data["stop_loss"],
                take_profit=row_data["take_profit"],
                close_time=row_data["close_time"],
                close_price=row_data["close_price"],
                commission=row_data["commission"],
                taxes=row_data["taxes"],
                swap=row_data["swap"],
                profit=row_data["profit"],
            )
        )

    return imported_rows


def _find_closed_trades_header_index(rows: list[list[str]]) -> int:
    for index, row in enumerate(rows):
        if _is_section_marker(row, "Closed Transactions:"):
            if index + 1 >= len(rows):
                break
            return index + 1

    raise ValueError("Closed Transactions section not found in MT4 statement.")


def _validate_mt4_header(header_row: list[str]) -> None:
    normalized_header = [_normalize_header_cell(value, position) for position, value in enumerate(header_row)]
    missing_fields = [field for field in ESSENTIAL_TRADE_FIELDS if field not in normalized_header]

    if missing_fields:
        missing_text = ", ".join(missing_fields)
        raise ValueError(f"MT4 statement is missing essential trade columns: {missing_text}")


def _normalize_header_cell(value: str, position: int) -> str:
    normalized = " ".join(value.replace("/", " ").split()).strip().lower()
    aliases = {
        "ticket": "ticket",
        "open time": "open_time",
        "type": "type",
        "size": "size",
        "item": "item",
        "price": "open_price" if position == 5 else "close_price",
        "s l": "stop_loss",
        "t p": "take_profit",
        "close time": "close_time",
        "commission": "commission",
        "taxes": "taxes",
        "swap": "swap",
        "profit": "profit",
    }
    return aliases.get(normalized, normalized.replace(" ", "_"))


def _is_section_marker(row: list[str], marker: str) -> bool:
    if not row:
        return False

    return row[0].strip() == marker and all(not cell.strip() for cell in row[1:])
