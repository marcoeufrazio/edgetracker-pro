import math

import pytest

from analytics.risk_metrics import calculate_mar_ratio, calculate_ulcer_index


def test_calculate_ulcer_index_matches_reference_formula() -> None:
    result = calculate_ulcer_index([0.0, 4.0, 3.0])

    expected = math.sqrt((0.0**2 + 4.0**2 + 3.0**2) / 3)
    assert result == pytest.approx(expected)


def test_calculate_ulcer_index_returns_zero_for_empty_series() -> None:
    assert calculate_ulcer_index([]) == 0.0


def test_calculate_mar_ratio_uses_total_return_over_max_drawdown_pct() -> None:
    result = calculate_mar_ratio(
        initial_balance=1000.0,
        equity_curve=[1100.0, 1050.0, 1200.0],
        max_drawdown_pct=10.0,
    )

    assert result == pytest.approx(2.0)


def test_calculate_mar_ratio_returns_zero_when_drawdown_is_zero() -> None:
    assert calculate_mar_ratio(1000.0, [1050.0], 0.0) == 0.0
