from __future__ import annotations

from database.models import AccountRecord, MetricRecord, ReportRecord, TradeRecord, UserRecord


def test_model_records_expose_expected_fields() -> None:
    user = UserRecord(id=1, name="Marco", email="marco@example.com", created_at="2026-03-15 10:00:00")
    account = AccountRecord(
        id=2,
        user_id=1,
        account_ref="24601985",
        broker="VT Markets",
        currency="USD",
        created_at="2026-03-15 10:01:00",
    )
    trade = TradeRecord(
        id=3,
        account_id=2,
        ticket=1001,
        symbol="EURUSD",
        trade_type="buy",
        open_time="2026-03-01 09:00:00",
        close_time="2026-03-01 10:00:00",
        volume=0.1,
        pnl=12.5,
        open_price=1.08,
        close_price=1.081,
        stop_loss=None,
        take_profit=1.082,
        commission=0.0,
        taxes=0.0,
        swap=0.0,
        source="mt4_html",
        source_type="buy",
        created_at="2026-03-15 10:02:00",
    )
    metric = MetricRecord(
        id=4,
        account_id=2,
        metric_name="traffic_light",
        metric_value="green",
        metric_type="str",
        created_at="2026-03-15 10:03:00",
    )
    report = ReportRecord(
        id=5,
        account_id=2,
        report_name="summary",
        report_type="markdown",
        generated_at="2026-03-15T10:04:00+00:00",
        content="# Report",
        created_at="2026-03-15 10:05:00",
    )

    assert user.email == "marco@example.com"
    assert account.account_ref == "24601985"
    assert trade.source == "mt4_html"
    assert metric.metric_type == "str"
    assert report.report_type == "markdown"
