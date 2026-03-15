from __future__ import annotations


GREEN_DRAWDOWN_PCT_LIMIT = 5.0
YELLOW_DRAWDOWN_PCT_LIMIT = 10.0


def classify_risk_zone(drawdown_pct: float) -> str:
    if drawdown_pct < GREEN_DRAWDOWN_PCT_LIMIT:
        return "green"
    if drawdown_pct < YELLOW_DRAWDOWN_PCT_LIMIT:
        return "yellow"
    return "red"
