from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthScoreResult:
    health_score: int
    health_classification: str


def calculate_health_score(
    *,
    profit_factor: float,
    expectancy: float,
    max_drawdown_pct: float,
    ulcer_index: float,
    risk_zone: str,
    traffic_light: str,
) -> HealthScoreResult:
    score = 0
    score += _score_profit_factor(profit_factor)
    score += _score_expectancy(expectancy)
    score += _score_max_drawdown_pct(max_drawdown_pct)
    score += _score_ulcer_index(ulcer_index)
    score += _score_risk_zone(risk_zone)
    score += _score_traffic_light(traffic_light)

    final_score = max(0, min(100, score))
    return HealthScoreResult(
        health_score=final_score,
        health_classification=_classify_health_score(final_score),
    )


def _score_profit_factor(value: float) -> int:
    if value >= 2.0:
        return 25
    if value >= 1.5:
        return 20
    if value >= 1.0:
        return 12
    return 0


def _score_expectancy(value: float) -> int:
    if value >= 0.20:
        return 20
    if value >= 0.05:
        return 15
    if value > 0:
        return 10
    if value == 0:
        return 5
    return 0


def _score_max_drawdown_pct(value: float) -> int:
    if value <= 5.0:
        return 20
    if value <= 10.0:
        return 14
    if value <= 20.0:
        return 8
    return 0


def _score_ulcer_index(value: float) -> int:
    if value <= 2.0:
        return 15
    if value <= 5.0:
        return 10
    if value <= 10.0:
        return 5
    return 0


def _score_risk_zone(value: str) -> int:
    scores = {"green": 10, "yellow": 5, "red": 0}
    return scores.get(value, 0)


def _score_traffic_light(value: str) -> int:
    scores = {"green": 10, "yellow": 5, "red": 0}
    return scores.get(value, 0)


def _classify_health_score(score: int) -> str:
    if score >= 80:
        return "excellent"
    if score >= 60:
        return "good"
    if score >= 40:
        return "warning"
    return "critical"
