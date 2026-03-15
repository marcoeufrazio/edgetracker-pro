from analytics.equity import calculate_current_profit, calculate_equity_curve


def test_calculate_equity_curve_returns_running_balance() -> None:
    result = calculate_equity_curve(initial_balance=1000, pnl_values=[100, -50, 25])

    assert result == [1100.0, 1050.0, 1075.0]


def test_calculate_current_profit_uses_last_equity_value() -> None:
    profit = calculate_current_profit(initial_balance=1000, equity_curve=[1100.0, 1050.0, 1075.0])

    assert profit == 75.0


def test_calculate_current_profit_returns_zero_for_empty_equity() -> None:
    assert calculate_current_profit(initial_balance=1000, equity_curve=[]) == 0.0
