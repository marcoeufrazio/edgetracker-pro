from __future__ import annotations


def calculate_green_target(cycle_target: float) -> float:
    return float(cycle_target) * 1.5


def calculate_traffic_light(current_profit: float, green_target: float) -> str:
    if current_profit < green_target * 0.6:
        return "red"
    if current_profit < green_target:
        return "yellow"
    return "green"
