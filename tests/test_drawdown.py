import pytest

from analytics.drawdown import calculate_drawdown


def test_calculate_drawdown_returns_absolute_and_percentage_series() -> None:
    result = calculate_drawdown([1100.0, 1050.0, 1200.0, 1140.0])

    assert result.drawdown_abs_series == [0.0, 50.0, 0.0, 60.0]
    assert result.drawdown_pct_series == pytest.approx([0.0, 4.5454545, 0.0, 5.0])
    assert result.max_drawdown_abs == 60.0
    assert result.max_drawdown_pct == 5.0


def test_calculate_drawdown_returns_zero_metrics_for_empty_series() -> None:
    result = calculate_drawdown([])

    assert result.drawdown_abs_series == []
    assert result.drawdown_pct_series == []
    assert result.max_drawdown_abs == 0.0
    assert result.max_drawdown_pct == 0.0
