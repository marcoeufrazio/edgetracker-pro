from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DrawdownResult:
    drawdown_abs_series: list[float]
    drawdown_pct_series: list[float]
    max_drawdown_abs: float
    max_drawdown_pct: float


@dataclass(frozen=True)
class AccountMetrics:
    equity: list[float]
    drawdown_abs_series: list[float]
    drawdown_pct_series: list[float]
    max_drawdown_abs: float
    max_drawdown_pct: float
    ulcer_index: float
    mar_ratio: float
    green_target: float
    traffic_light: str
    health_summary: str
