from __future__ import annotations

from dataclasses import dataclass

from analytics.performance import calculate_performance_metrics
from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class SyntheticRSummary:
    average_loss: float
    average_r: float
    best_r: float
    worst_r: float
    distribution_r: dict[str, int]


def calculate_synthetic_r_multiple(trades: list[NormalizedTrade]) -> tuple[list[float], SyntheticRSummary]:
    performance = calculate_performance_metrics(trades)
    average_loss = performance.average_loss

    if average_loss <= 0:
        return [], SyntheticRSummary(
            average_loss=0.0,
            average_r=0.0,
            best_r=0.0,
            worst_r=0.0,
            distribution_r={},
        )

    r_values = [trade.net_profit / average_loss for trade in trades]
    distribution_r = _build_distribution(r_values)

    return r_values, SyntheticRSummary(
        average_loss=average_loss,
        average_r=sum(r_values) / len(r_values) if r_values else 0.0,
        best_r=max(r_values, default=0.0),
        worst_r=min(r_values, default=0.0),
        distribution_r=distribution_r,
    )


def _build_distribution(r_values: list[float]) -> dict[str, int]:
    distribution = {
        "<=-2R": 0,
        "-2R to -1R": 0,
        "-1R to 0R": 0,
        "0R to 1R": 0,
        "1R to 2R": 0,
        ">=2R": 0,
    }

    for value in r_values:
        if value <= -2:
            distribution["<=-2R"] += 1
        elif value < -1:
            distribution["-2R to -1R"] += 1
        elif value < 0:
            distribution["-1R to 0R"] += 1
        elif value < 1:
            distribution["0R to 1R"] += 1
        elif value < 2:
            distribution["1R to 2R"] += 1
        else:
            distribution[">=2R"] += 1

    return distribution
