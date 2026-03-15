from __future__ import annotations

from datetime import datetime

from analytics.trade_schema import ImportedTradeRow, NormalizedTrade


def normalize_mt4_trades(trades: list[ImportedTradeRow]) -> list[NormalizedTrade]:
    return [normalize_mt4_trade(trade) for trade in trades]


def normalize_mt4_trade(trade: ImportedTradeRow) -> NormalizedTrade:
    commission = _parse_float(trade.commission)
    taxes = _parse_float(trade.taxes)
    swap = _parse_float(trade.swap)
    profit = _parse_float(trade.profit)

    return NormalizedTrade(
        ticket=int(trade.ticket),
        opened_at=_parse_datetime(trade.open_time),
        closed_at=_parse_datetime(trade.close_time),
        side=trade.trade_type.strip().lower(),
        size_lots=_parse_float(trade.size),
        symbol=_normalize_symbol(trade.item),
        open_price=_parse_float(trade.open_price),
        stop_loss=_parse_optional_float(trade.stop_loss),
        take_profit=_parse_optional_float(trade.take_profit),
        close_price=_parse_float(trade.close_price),
        commission=commission,
        taxes=taxes,
        swap=swap,
        profit=profit,
        net_profit=commission + taxes + swap + profit,
        source="mt4_html",
        source_type=trade.trade_type.strip().lower(),
    )


def _parse_datetime(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y.%m.%d %H:%M:%S")


def _parse_float(value: str) -> float:
    cleaned = value.strip().replace(",", "")
    return float(cleaned)


def _parse_optional_float(value: str) -> float | None:
    parsed_value = _parse_float(value)
    if parsed_value == 0.0:
        return None
    return parsed_value


def _normalize_symbol(value: str) -> str:
    base_symbol = value.strip().split("-", maxsplit=1)[0]
    return base_symbol.upper()
