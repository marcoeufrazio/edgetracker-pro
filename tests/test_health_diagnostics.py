from analytics.health_diagnostics import build_health_diagnostic_text


def test_build_health_diagnostic_text_highlights_strong_state() -> None:
    text = build_health_diagnostic_text(
        health_classification="excellent",
        profit_factor=2.0,
        expectancy=0.2,
        max_drawdown_pct=4.0,
        ulcer_index=1.2,
        risk_zone="green",
        traffic_light="green",
    )

    assert "excellent" in text.lower()
    assert "profitability is strong" in text.lower()
    assert "risk is controlled" in text.lower()


def test_build_health_diagnostic_text_highlights_weak_state() -> None:
    text = build_health_diagnostic_text(
        health_classification="critical",
        profit_factor=0.7,
        expectancy=-0.2,
        max_drawdown_pct=15.0,
        ulcer_index=6.0,
        risk_zone="red",
        traffic_light="red",
    )

    assert "critical" in text.lower()
    assert "profitability is weak" in text.lower()
    assert "requires corrective action" in text.lower()
