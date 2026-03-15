from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


MT4_CLOSED_TRADES_HEADERS = [
    "ticket",
    "open_time",
    "type",
    "size",
    "item",
    "open_price",
    "stop_loss",
    "take_profit",
    "close_time",
    "close_price",
    "commission",
    "taxes",
    "swap",
    "profit",
]

ESSENTIAL_TRADE_FIELDS = (
    "ticket",
    "open_time",
    "type",
    "size",
    "item",
    "open_price",
    "close_time",
    "close_price",
    "profit",
)


@dataclass(frozen=True)
class ImportedTradeRow:
    ticket: str
    open_time: str
    trade_type: str
    size: str
    item: str
    open_price: str
    stop_loss: str
    take_profit: str
    close_time: str
    close_price: str
    commission: str
    taxes: str
    swap: str
    profit: str


@dataclass(frozen=True)
class NormalizedTrade:
    ticket: int
    opened_at: datetime
    closed_at: datetime
    side: str
    size_lots: float
    symbol: str
    open_price: float
    stop_loss: float | None
    take_profit: float | None
    close_price: float
    commission: float
    taxes: float
    swap: float
    profit: float
    net_profit: float
    source: str
    source_type: str


@dataclass(frozen=True)
class EquityTimelinePoint:
    trade_number: int
    close_time: datetime
    pnl: float
    cumulative_pnl: float
    equity: float


@dataclass(frozen=True)
class DrawdownTimelinePoint:
    trade_number: int
    close_time: datetime
    pnl: float
    cumulative_pnl: float
    equity: float
    peak_equity: float
    drawdown_abs: float
    drawdown_pct: float
    risk_zone: str
