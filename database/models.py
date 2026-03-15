from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserRecord:
    id: int | None
    name: str
    email: str


@dataclass(frozen=True)
class AccountRecord:
    id: int | None
    user_id: int
    account_ref: str
    broker: str | None
    currency: str | None


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


@dataclass(frozen=True)
class MetricRecord:
    id: int | None
    account_id: int
    metric_name: str
    metric_value: float
