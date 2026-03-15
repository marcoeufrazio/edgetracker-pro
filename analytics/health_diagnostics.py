from __future__ import annotations


def build_health_diagnostic_text(
    *,
    health_classification: str,
    profit_factor: float,
    expectancy: float,
    max_drawdown_pct: float,
    ulcer_index: float,
    risk_zone: str,
    traffic_light: str,
) -> str:
    summary = _classification_summary(health_classification)
    performance = _performance_message(profit_factor, expectancy)
    risk = _risk_message(max_drawdown_pct, ulcer_index, risk_zone)
    execution = _execution_message(traffic_light)
    return f"{summary} {performance} {risk} {execution}"


def _classification_summary(value: str) -> str:
    summaries = {
        "excellent": "Trading health is excellent.",
        "good": "Trading health is good.",
        "warning": "Trading health needs attention.",
        "critical": "Trading health is critical.",
    }
    return summaries.get(value, "Trading health is undefined.")


def _performance_message(profit_factor: float, expectancy: float) -> str:
    if profit_factor >= 1.5 and expectancy > 0:
        return "Profitability is strong and trade expectancy is positive."
    if profit_factor >= 1.0 and expectancy >= 0:
        return "Profitability is stable but still has room to improve."
    return "Profitability is weak and expectancy is under pressure."


def _risk_message(max_drawdown_pct: float, ulcer_index: float, risk_zone: str) -> str:
    if risk_zone == "green" and max_drawdown_pct <= 5 and ulcer_index <= 2:
        return "Risk is controlled with shallow drawdowns."
    if risk_zone == "yellow" or max_drawdown_pct <= 10 or ulcer_index <= 5:
        return "Risk is moderate and should be monitored closely."
    return "Risk is elevated with meaningful drawdown stress."


def _execution_message(traffic_light: str) -> str:
    if traffic_light == "green":
        return "Account momentum is aligned with the current target."
    if traffic_light == "yellow":
        return "Account momentum is below target but still recoverable."
    return "Account momentum is below target and requires corrective action."
