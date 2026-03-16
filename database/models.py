from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserRecord:
    id: int | None
    name: str
    email: str
    created_at: str | None = None


@dataclass(frozen=True)
class AccountRecord:
    id: int | None
    user_id: int
    account_ref: str
    broker: str | None
    currency: str | None
    statement_path: str | None = None
    created_at: str | None = None


@dataclass(frozen=True)
class TradeRecord:
    id: int | None
    account_id: int
    ticket: int
    symbol: str
    trade_type: str
    open_time: str
    close_time: str
    volume: float
    pnl: float
    open_price: float
    close_price: float
    stop_loss: float | None
    take_profit: float | None
    commission: float
    taxes: float
    swap: float
    source: str
    source_type: str
    created_at: str | None = None


@dataclass(frozen=True)
class MetricRecord:
    id: int | None
    account_id: int
    metric_name: str
    metric_value: str
    metric_type: str
    created_at: str | None = None


@dataclass(frozen=True)
class ReportRecord:
    id: int | None
    account_id: int
    report_name: str
    report_type: str
    generated_at: str
    content: str
    created_at: str | None = None
