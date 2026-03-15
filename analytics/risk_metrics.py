from __future__ import annotations

import math


def calculate_ulcer_index(drawdown_pct_series: list[float]) -> float:
    if not drawdown_pct_series:
        return 0.0

    squared_sum = sum(value**2 for value in drawdown_pct_series)
    return math.sqrt(squared_sum / len(drawdown_pct_series))


def calculate_mar_ratio(initial_balance: float, equity_curve: list[float], max_drawdown_pct: float) -> float:
    if not equity_curve or max_drawdown_pct <= 0:
        return 0.0

    ending_balance = equity_curve[-1]
    if initial_balance <= 0:
        return 0.0

    total_return_pct = ((ending_balance - initial_balance) / initial_balance) * 100
    return total_return_pct / max_drawdown_pct
