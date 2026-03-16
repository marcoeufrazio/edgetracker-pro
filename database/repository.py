from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

from analytics.trade_schema import NormalizedTrade
from analytics.types import AccountMetrics
from database.models import AccountRecord, MetricRecord, ReportRecord, TradeRecord, UserRecord


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class Repository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_user(self, name: str, email: str) -> UserRecord:
        cursor = self.connection.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email),
        )
        self.connection.commit()
        return self.get_user(cursor.lastrowid)

    def get_user(self, user_id: int) -> UserRecord:
        row = self.connection.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"User not found: {user_id}")
        return UserRecord(
            id=int(row["id"]),
            name=str(row["name"]),
            email=str(row["email"]),
            created_at=str(row["created_at"]),
        )

    def create_account(
        self,
        user_id: int,
        account_ref: str,
        broker: str | None = None,
        currency: str | None = None,
        statement_path: str | None = None,
    ) -> AccountRecord:
        cursor = self.connection.execute(
            "INSERT INTO accounts (user_id, account_ref, broker, currency, statement_path) VALUES (?, ?, ?, ?, ?)",
            (user_id, account_ref, broker, currency, statement_path),
        )
        self.connection.commit()
        return self.get_account(cursor.lastrowid)

    def save_account(
        self,
        user_id: int,
        account_ref: str,
        broker: str | None = None,
        currency: str | None = None,
        statement_path: str | None = None,
    ) -> AccountRecord:
        self.connection.execute(
            """
            INSERT INTO accounts (user_id, account_ref, broker, currency, statement_path)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, account_ref)
            DO UPDATE SET
                broker = excluded.broker,
                currency = excluded.currency,
                statement_path = COALESCE(excluded.statement_path, accounts.statement_path)
            """,
            (user_id, account_ref, broker, currency, statement_path),
        )
        self.connection.commit()
        return self.get_account_for_user(user_id, account_ref)

    def get_account(self, account_id: int) -> AccountRecord:
        row = self.connection.execute(
            """
            SELECT id, user_id, account_ref, broker, currency, statement_path, created_at
            FROM accounts
            WHERE id = ?
            """,
            (account_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Account not found: {account_id}")
        return _account_from_row(row)

    def list_accounts(self, user_id: int | None = None) -> list[AccountRecord]:
        if user_id is None:
            rows = self.connection.execute(
                """
                SELECT id, user_id, account_ref, broker, currency, statement_path, created_at
                FROM accounts
                ORDER BY id
                """
            ).fetchall()
        else:
            rows = self.connection.execute(
                """
                SELECT id, user_id, account_ref, broker, currency, statement_path, created_at
                FROM accounts
                WHERE user_id = ?
                ORDER BY id
                """,
                (user_id,),
            ).fetchall()
        return [_account_from_row(row) for row in rows]

    def get_account_for_user(self, user_id: int, account_ref: str) -> AccountRecord:
        row = self.connection.execute(
            """
            SELECT id, user_id, account_ref, broker, currency, statement_path, created_at
            FROM accounts
            WHERE user_id = ? AND account_ref = ?
            """,
            (user_id, account_ref),
        ).fetchone()
        if row is None:
            raise ValueError(f"Account not found for user: {user_id}/{account_ref}")
        return _account_from_row(row)

    def account_exists_for_ref(self, account_ref: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM accounts WHERE account_ref = ? LIMIT 1",
            (account_ref,),
        ).fetchone()
        return row is not None

    def save_trades(self, account_id: int, trades: list[NormalizedTrade]) -> list[TradeRecord]:
        records: list[TradeRecord] = []
        for trade in trades:
            cursor = self.connection.execute(
                """
                INSERT INTO trades (
                    account_id,
                    ticket,
                    symbol,
                    trade_type,
                    open_time,
                    close_time,
                    volume,
                    pnl,
                    open_price,
                    close_price,
                    stop_loss,
                    take_profit,
                    commission,
                    taxes,
                    swap,
                    source,
                    source_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    trade.open_price,
                    trade.close_price,
                    trade.stop_loss,
                    trade.take_profit,
                    trade.commission,
                    trade.taxes,
                    trade.swap,
                    trade.source,
                    trade.source_type,
                ),
            )
            records.append(self.get_trade(int(cursor.lastrowid)))

        self.connection.commit()
        return records

    def get_trade(self, trade_id: int) -> TradeRecord:
        row = self.connection.execute(
            """
            SELECT
                id,
                account_id,
                ticket,
                symbol,
                trade_type,
                open_time,
                close_time,
                volume,
                pnl,
                open_price,
                close_price,
                stop_loss,
                take_profit,
                commission,
                taxes,
                swap,
                source,
                source_type,
                created_at
            FROM trades
            WHERE id = ?
            """,
            (trade_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Trade not found: {trade_id}")
        return _trade_from_row(row)

    def list_trades(self, account_id: int) -> list[TradeRecord]:
        rows = self.connection.execute(
            """
            SELECT
                id,
                account_id,
                ticket,
                symbol,
                trade_type,
                open_time,
                close_time,
                volume,
                pnl,
                open_price,
                close_price,
                stop_loss,
                take_profit,
                commission,
                taxes,
                swap,
                source,
                source_type,
                created_at
            FROM trades
            WHERE account_id = ?
            ORDER BY close_time, ticket
            """,
            (account_id,),
        ).fetchall()
        return [_trade_from_row(row) for row in rows]

    def save_metrics(self, account_id: int, metrics: AccountMetrics) -> list[MetricRecord]:
        metric_map = {
            "equity": metrics.equity,
            "drawdown_abs_series": metrics.drawdown_abs_series,
            "drawdown_pct_series": metrics.drawdown_pct_series,
            "max_drawdown_abs": metrics.max_drawdown_abs,
            "max_drawdown_pct": metrics.max_drawdown_pct,
            "ulcer_index": metrics.ulcer_index,
            "mar_ratio": metrics.mar_ratio,
            "green_target": metrics.green_target,
            "traffic_light": metrics.traffic_light,
            "health_summary": metrics.health_summary,
        }
        return self._upsert_metric_map(account_id, metric_map)

    def save_account_metrics(self, account_id: int, metrics: AccountMetrics) -> list[MetricRecord]:
        metric_map = {
            "max_drawdown_abs": metrics.max_drawdown_abs,
            "max_drawdown_pct": metrics.max_drawdown_pct,
            "ulcer_index": metrics.ulcer_index,
            "mar_ratio": metrics.mar_ratio,
            "green_target": metrics.green_target,
        }
        return self._upsert_metric_map(account_id, metric_map)

    def get_account_metrics(self, account_id: int) -> dict[str, object]:
        rows = self.connection.execute(
            """
            SELECT id, account_id, metric_name, metric_value, metric_type, created_at
            FROM metrics
            WHERE account_id = ?
            ORDER BY metric_name
            """,
            (account_id,),
        ).fetchall()
        return {str(row["metric_name"]): _deserialize_metric_value(str(row["metric_value"]), str(row["metric_type"])) for row in rows}

    def get_metric_records(self, account_id: int) -> list[MetricRecord]:
        rows = self.connection.execute(
            """
            SELECT id, account_id, metric_name, metric_value, metric_type, created_at
            FROM metrics
            WHERE account_id = ?
            ORDER BY metric_name
            """,
            (account_id,),
        ).fetchall()
        return [_metric_from_row(row) for row in rows]

    def get_metric_record(self, account_id: int, metric_name: str) -> MetricRecord:
        row = self.connection.execute(
            """
            SELECT id, account_id, metric_name, metric_value, metric_type, created_at
            FROM metrics
            WHERE account_id = ? AND metric_name = ?
            """,
            (account_id, metric_name),
        ).fetchone()
        if row is None:
            raise ValueError(f"Metric not found: {account_id}/{metric_name}")
        return _metric_from_row(row)

    def save_report(
        self,
        account_id: int,
        report_name: str,
        content: str,
        report_type: str = "markdown",
        generated_at: str | None = None,
    ) -> ReportRecord:
        report_generated_at = generated_at or _utc_now()
        cursor = self.connection.execute(
            """
            INSERT INTO reports (account_id, report_name, report_type, generated_at, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (account_id, report_name, report_type, report_generated_at, content),
        )
        self.connection.commit()
        return self.get_report(int(cursor.lastrowid))

    def get_report(self, report_id: int) -> ReportRecord:
        row = self.connection.execute(
            """
            SELECT id, account_id, report_name, report_type, generated_at, content, created_at
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Report not found: {report_id}")
        return _report_from_row(row)

    def list_reports(self, account_id: int) -> list[ReportRecord]:
        rows = self.connection.execute(
            """
            SELECT id, account_id, report_name, report_type, generated_at, content, created_at
            FROM reports
            WHERE account_id = ?
            ORDER BY id
            """,
            (account_id,),
        ).fetchall()
        return [_report_from_row(row) for row in rows]

    def count_rows(self, table_name: str) -> int:
        allowed_tables = {"users", "accounts", "trades", "metrics", "reports"}
        if table_name not in allowed_tables:
            raise ValueError(f"Unsupported table name: {table_name}")

        row = self.connection.execute(f"SELECT COUNT(*) AS row_count FROM {table_name}").fetchone()
        if row is None:
            return 0
        return int(row["row_count"])

    def _upsert_metric_map(self, account_id: int, metric_map: dict[str, object]) -> list[MetricRecord]:
        records: list[MetricRecord] = []
        for metric_name, metric_value in metric_map.items():
            serialized_value, metric_type = _serialize_metric_value(metric_value)
            self.connection.execute(
                """
                INSERT INTO metrics (account_id, metric_name, metric_value, metric_type)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(account_id, metric_name)
                DO UPDATE SET
                    metric_value = excluded.metric_value,
                    metric_type = excluded.metric_type
                """,
                (account_id, metric_name, serialized_value, metric_type),
            )
            records.append(self.get_metric_record(account_id, metric_name))

        self.connection.commit()
        return records


def _serialize_metric_value(value: object) -> tuple[str, str]:
    if isinstance(value, str):
        return value, "str"
    if isinstance(value, (int, float)):
        return str(value), "float"
    return json.dumps(value), "json"


def _deserialize_metric_value(value: str, metric_type: str) -> object:
    if metric_type == "str":
        return value
    if metric_type == "float":
        return float(value)
    if metric_type == "json":
        return json.loads(value)
    raise ValueError(f"Unsupported metric type: {metric_type}")


def _account_from_row(row: sqlite3.Row) -> AccountRecord:
    return AccountRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        account_ref=str(row["account_ref"]),
        broker=row["broker"],
        currency=row["currency"],
        statement_path=row["statement_path"],
        created_at=str(row["created_at"]),
    )


def _trade_from_row(row: sqlite3.Row) -> TradeRecord:
    return TradeRecord(
        id=int(row["id"]),
        account_id=int(row["account_id"]),
        ticket=int(row["ticket"]),
        symbol=str(row["symbol"]),
        trade_type=str(row["trade_type"]),
        open_time=str(row["open_time"]),
        close_time=str(row["close_time"]),
        volume=float(row["volume"]),
        pnl=float(row["pnl"]),
        open_price=float(row["open_price"]),
        close_price=float(row["close_price"]),
        stop_loss=float(row["stop_loss"]) if row["stop_loss"] is not None else None,
        take_profit=float(row["take_profit"]) if row["take_profit"] is not None else None,
        commission=float(row["commission"]),
        taxes=float(row["taxes"]),
        swap=float(row["swap"]),
        source=str(row["source"]),
        source_type=str(row["source_type"]),
        created_at=str(row["created_at"]),
    )


def _metric_from_row(row: sqlite3.Row) -> MetricRecord:
    return MetricRecord(
        id=int(row["id"]),
        account_id=int(row["account_id"]),
        metric_name=str(row["metric_name"]),
        metric_value=str(row["metric_value"]),
        metric_type=str(row["metric_type"]),
        created_at=str(row["created_at"]),
    )


def _report_from_row(row: sqlite3.Row) -> ReportRecord:
    return ReportRecord(
        id=int(row["id"]),
        account_id=int(row["account_id"]),
        report_name=str(row["report_name"]),
        report_type=str(row["report_type"]),
        generated_at=str(row["generated_at"]),
        content=str(row["content"]),
        created_at=str(row["created_at"]),
    )
