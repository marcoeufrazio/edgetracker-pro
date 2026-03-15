from datetime import datetime

from analytics.chart_export import export_chart
from analytics.charts import create_equity_curve_chart
from analytics.trade_schema import EquityTimelinePoint


def test_export_chart_writes_png_file(tmp_path) -> None:
    timeline = [
        EquityTimelinePoint(1, datetime(2026, 3, 1, 10, 0, 0), 10.0, 10.0, 1010.0),
        EquityTimelinePoint(2, datetime(2026, 3, 1, 11, 0, 0), 5.0, 15.0, 1015.0),
    ]
    figure = create_equity_curve_chart(timeline)

    output_path = tmp_path / "charts" / "equity_curve.png"
    exported_path = export_chart(figure, output_path)

    assert exported_path == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0
