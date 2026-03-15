from __future__ import annotations


def build_health_summary(
    traffic_light: str,
    current_profit: float,
    green_target: float,
    max_drawdown_pct: float,
    ulcer_index: float,
) -> str:
    return (
        f"Status={traffic_light}; "
        f"profit={current_profit:.2f}; "
        f"green_target={green_target:.2f}; "
        f"max_drawdown_pct={max_drawdown_pct:.2f}; "
        f"ulcer_index={ulcer_index:.2f}"
    )
