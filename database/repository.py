from __future__ import annotations

import sqlite3

from analytics.trade_schema import NormalizedTrade
from analytics.types import AccountMetrics
from database.models import AccountRecord, MetricRecord, TradeRecord, UserRecord


class Repository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_user(self, name: str, email: str) -> UserRecord:
        cursor = self.connection.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email),
        )
        self.connection.commit()
        return UserRecord(id=cursor.lastrowid, name=name, email=email)

    def create_account(
        self,
        user_id: int,
        account_ref: str,
        broker: str | None = None,
        currency: str | None = None,
    ) -> AccountRecord:
        cursor = self.connection.execute(
            "INSERT INTO accounts (user_id, account_ref, broker, currency) VALUES (?, ?, ?, ?)",
            (user_id, account_ref, broker, currency),
        )
        self.connection.commit()
        return AccountRecord(
            id=cursor.lastrowid,
            user_id=user_id,
            account_ref=account_ref,
            broker=broker,
            currency=currency,
        )

    def save_trades(self, account_id: int, trades: list[NormalizedTrade]) -> list[TradeRecord]:
        records: list[TradeRecord] = []
        for trade in trades:
            cursor = self.connection.execute(
                """
                INSERT INTO trades (
                    account_id, ticket, symbol, trade_type, open_time, close_time, volume, pnl
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    trade.ticket,
                    trade.symbol,
                    trade.side,
                    trade.opened_at.isoformat(sep=" "),
                    trade.closed_at.isoformat(sep=" "),
                    trade.size_lots,
                    trade.net_profit,
                ),
            )
            records.append(
                TradeRecord(
                    id=cursor.lastrowid,
                    account_id=account_id,
                    ticket=trade.ticket,
                    symbol=trade.symbol,
                    trade_type=trade.side,
                    open_time=trade.opened_at.isoformat(sep=" "),
                    close_time=trade.closed_at.isoformat(sep=" "),
                    volume=trade.size_lots,
                    pnl=trade.net_profit,
                )
            )

        self.connection.commit()
        return records

    def save_account_metrics(self, account_id: int, metrics: AccountMetrics) -> list[MetricRecord]:
        metric_map = {
            "max_drawdown_abs": metrics.max_drawdown_abs,
            "max_drawdown_pct": metrics.max_drawdown_pct,
            "ulcer_index": metrics.ulcer_index,
            "mar_ratio": metrics.mar_ratio,
            "green_target": metrics.green_target,
        }

        records: list[MetricRecord] = []
        for metric_name, metric_value in metric_map.items():
            cursor = self.connection.execute(
                "INSERT INTO metrics (account_id, metric_name, metric_value) VALUES (?, ?, ?)",
                (account_id, metric_name, metric_value),
            )
            records.append(
                MetricRecord(
                    id=cursor.lastrowid,
                    account_id=account_id,
                    metric_name=metric_name,
                    metric_value=float(metric_value),
                )
            )

        self.connection.commit()
        return records

    def count_rows(self, table_name: str) -> int:
        row = self.connection.execute(f"SELECT COUNT(*) AS row_count FROM {table_name}").fetchone()
        return int(row["row_count"])
