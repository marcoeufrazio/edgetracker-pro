from __future__ import annotations


def calculate_equity_curve(initial_balance: float, pnl_values: list[float]) -> list[float]:
    equity: list[float] = []
    current_equity = float(initial_balance)

    for pnl in pnl_values:
        current_equity += pnl
        equity.append(current_equity)

    return equity


def calculate_current_profit(initial_balance: float, equity_curve: list[float]) -> float:
    if not equity_curve:
        return 0.0

    return equity_curve[-1] - float(initial_balance)
