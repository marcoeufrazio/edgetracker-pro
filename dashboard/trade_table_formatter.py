from __future__ import annotations

import pandas as pd


def format_trade_table_for_display(trade_table: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    table = trade_table.copy()

    rename_map = {
        "ticket": "Ticket",
        "symbol": "Symbol",
        "type": "Type",
        "open_time": "Open Time",
        "close_time": "Close Time",
        "pnl": "PnL",
        "volume": "Volume",
        "duration_minutes": "Duration",
        "r_multiple": "R Multiple",
    }
    table = table.rename(columns=rename_map)

    pnl_raw = table["PnL"].copy() if "PnL" in table.columns else pd.Series(index=table.index, dtype=float)

    if "PnL" in table.columns:
        table["PnL"] = table["PnL"].map(_format_pnl)

    if "Volume" in table.columns:
        table["Volume"] = table["Volume"].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

    if "Duration" in table.columns:
        table["Duration"] = table["Duration"].map(_format_duration)

    if "R Multiple" in table.columns:
        table["R Multiple"] = table["R Multiple"].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

    if "Type" in table.columns:
        table["Type"] = table["Type"].map(_format_trade_type)

    if "Symbol" in table.columns:
        table["Symbol"] = table["Symbol"].map(_format_symbol_badge)

    display_columns = [
        "Ticket",
        "Symbol",
        "Type",
        "Open Time",
        "Close Time",
        "PnL",
        "Volume",
        "Duration",
    ]

    if "R Multiple" in table.columns:
        display_columns.append("R Multiple")

    return table[display_columns], pnl_raw


def _format_pnl(value) -> str:
    if pd.isna(value):
        return ""
    if value > 0:
        return f"🟢 +{value:.2f}"
    if value < 0:
        return f"🔴 {value:.2f}"
    return f"{value:.2f}"


def _format_duration(minutes) -> str:
    if pd.isna(minutes):
        return ""
    total_seconds = int(round(float(minutes) * 60))
    m = total_seconds // 60
    s = total_seconds % 60
    return f"{m}:{s:02d}"


def _format_trade_type(value: str) -> str:
    if not value:
        return ""
    value_lower = str(value).lower()
    if value_lower == "buy":
        return "🟢 BUY"
    if value_lower == "sell":
        return "🔴 SELL"
    return str(value).upper()


def _format_symbol_badge(value: str) -> str:
    if not value:
        return ""
    symbol = str(value).upper()
    symbol_icons = {
        "EURUSD": "💶 EURUSD",
        "GBPUSD": "💷 GBPUSD",
        "USDJPY": "💴 USDJPY",
        "XAUUSD": "🥇 XAUUSD",
        "US30": "🇺🇸 US30",
        "NAS100": "💻 NAS100",
        "SPX500": "📊 SPX500",
    }
    return symbol_icons.get(symbol, f"🏷️ {symbol}")