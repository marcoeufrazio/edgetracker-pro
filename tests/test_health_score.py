from analytics.health_score import calculate_health_score


def test_calculate_health_score_returns_excellent_for_strong_inputs() -> None:
    result = calculate_health_score(
        profit_factor=2.1,
        expectancy=0.25,
        max_drawdown_pct=4.0,
        ulcer_index=1.5,
        risk_zone="green",
        traffic_light="green",
    )

    assert result.health_score == 100
    assert result.health_classification == "excellent"


def test_calculate_health_score_returns_critical_for_weak_inputs() -> None:
    result = calculate_health_score(
        profit_factor=0.8,
        expectancy=-0.1,
        max_drawdown_pct=18.0,
        ulcer_index=7.0,
        risk_zone="red",
        traffic_light="red",
    )

    assert result.health_score == 13
    assert result.health_classification == "critical"
