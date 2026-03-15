from datetime import datetime

from matplotlib.figure import Figure

from analytics.charts import create_drawdown_curve_chart, create_equity_curve_chart
from analytics.trade_schema import DrawdownTimelinePoint, EquityTimelinePoint


def test_create_equity_curve_chart_returns_figure_with_line_data() -> None:
    timeline = [
        EquityTimelinePoint(1, datetime(2026, 3, 1, 10, 0, 0), 10.0, 10.0, 1010.0),
        EquityTimelinePoint(2, datetime(2026, 3, 1, 11, 0, 0), -5.0, 5.0, 1005.0),
    ]

    figure = create_equity_curve_chart(timeline)

    assert isinstance(figure, Figure)
    assert len(figure.axes) == 1
    assert len(figure.axes[0].lines) == 1


def test_create_drawdown_curve_chart_returns_figure_with_line_data() -> None:
    series = [
        DrawdownTimelinePoint(1, datetime(2026, 3, 1, 10, 0, 0), 10.0, 10.0, 1010.0, 1010.0, 0.0, 0.0, "green"),
        DrawdownTimelinePoint(2, datetime(2026, 3, 1, 11, 0, 0), -20.0, -10.0, 990.0, 1010.0, 20.0, 1.98, "green"),
    ]

    figure = create_drawdown_curve_chart(series)

    assert isinstance(figure, Figure)
    assert len(figure.axes) == 1
    assert len(figure.axes[0].lines) == 1
