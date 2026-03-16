from __future__ import annotations

import sqlite3
from pathlib import Path


DEFAULT_DATABASE_NAME = "edgetracker_pro.db"


def connect_db(database_path: str | Path) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_ref TEXT NOT NULL,
            broker TEXT,
            currency TEXT,
            statement_path TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, account_ref),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            ticket INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            trade_type TEXT NOT NULL,
            open_time TEXT NOT NULL,
            close_time TEXT NOT NULL,
            volume REAL NOT NULL,
            pnl REAL NOT NULL,
            open_price REAL NOT NULL,
            close_price REAL NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            commission REAL NOT NULL,
            taxes REAL NOT NULL,
            swap REAL NOT NULL,
            source TEXT NOT NULL,
            source_type TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account_id, ticket, open_time, close_time),
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account_id, metric_name),
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            report_name TEXT NOT NULL,
            report_type TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
        CREATE INDEX IF NOT EXISTS idx_trades_account_id ON trades(account_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_account_id ON metrics(account_id);
        CREATE INDEX IF NOT EXISTS idx_reports_account_id ON reports(account_id);
        """
    )
    _ensure_column_exists(connection, "users", "password_hash", "TEXT")
    _ensure_column_exists(connection, "accounts", "statement_path", "TEXT")
    connection.commit()


def _ensure_column_exists(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {str(row["name"]) for row in rows}
    if column_name in existing_columns:
        return

    connection.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
    )
