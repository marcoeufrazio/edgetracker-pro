from __future__ import annotations

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from analytics.trade_schema import DrawdownTimelinePoint, EquityTimelinePoint


def create_equity_curve_chart(timeline: list[EquityTimelinePoint]) -> Figure:
    figure = Figure(figsize=(10, 4.5), tight_layout=True)
    FigureCanvasAgg(figure)
    axis = figure.add_subplot(1, 1, 1)

    x_values = [point.close_time for point in timeline]
    y_values = [point.equity for point in timeline]

    axis.plot(x_values, y_values, color="#1f6f8b", linewidth=2)
    axis.set_title("Equity Curve")
    axis.set_xlabel("Close Time")
    axis.set_ylabel("Equity")
    axis.grid(True, alpha=0.3)

    return figure


def create_drawdown_curve_chart(series: list[DrawdownTimelinePoint]) -> Figure:
    figure = Figure(figsize=(10, 4.5), tight_layout=True)
    FigureCanvasAgg(figure)
    axis = figure.add_subplot(1, 1, 1)

    x_values = [point.close_time for point in series]
    y_values = [point.drawdown_pct for point in series]

    axis.plot(x_values, y_values, color="#b83b5e", linewidth=2)
    axis.fill_between(x_values, y_values, 0, color="#f08a5d", alpha=0.25)
    axis.set_title("Drawdown Curve")
    axis.set_xlabel("Close Time")
    axis.set_ylabel("Drawdown %")
    axis.grid(True, alpha=0.3)

    return figure
