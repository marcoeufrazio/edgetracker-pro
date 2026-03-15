from datetime import datetime
from pathlib import Path

import pytest

from analytics.drawdown_series import build_drawdown_series, build_drawdown_series_from_mt4_statement
from analytics.trade_schema import EquityTimelinePoint


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_build_drawdown_series_adds_peak_and_drawdown_fields() -> None:
    timeline = [
        EquityTimelinePoint(1, datetime(2026, 3, 1, 10, 0, 0), 20.0, 20.0, 1020.0),
        EquityTimelinePoint(2, datetime(2026, 3, 1, 11, 0, 0), -50.0, -30.0, 970.0),
        EquityTimelinePoint(3, datetime(2026, 3, 1, 12, 0, 0), 10.0, -20.0, 980.0),
    ]

    series = build_drawdown_series(timeline)

    assert [point.peak_equity for point in series] == pytest.approx([1020.0, 1020.0, 1020.0])
    assert [point.drawdown_abs for point in series] == pytest.approx([0.0, 50.0, 40.0])
    assert [point.drawdown_pct for point in series] == pytest.approx([0.0, 4.9019608, 3.9215686])
    assert [point.risk_zone for point in series] == ["green", "green", "green"]


def test_build_drawdown_series_from_mt4_statement_reads_sample_html() -> None:
    series = build_drawdown_series_from_mt4_statement(
        path=SAMPLE_STATEMENT_PATH,
        initial_balance=1000.0,
    )

    assert series
    assert series[0].trade_number == 1
    assert series[-1].equity == pytest.approx(994.49)
    assert max(point.drawdown_pct for point in series) > 0
