from dataclasses import dataclass


@dataclass
class EdgeScoreResult:
    score: int
    classification: str
    summary: str


def calculate_edge_score(
    profit_factor: float | None,
    expectancy: float | None,
    win_rate: float | None,
    max_drawdown_pct: float | None,
    ulcer_index: float | None,
) -> EdgeScoreResult:
    score = 0

    # Profit Factor (0-25)
    if profit_factor is not None:
        if profit_factor >= 2.0:
            score += 25
        elif profit_factor >= 1.5:
            score += 20
        elif profit_factor >= 1.2:
            score += 15
        elif profit_factor >= 1.0:
            score += 10
        else:
            score += 0

    # Expectancy (0-20)
    if expectancy is not None:
        if expectancy >= 0.5:
            score += 20
        elif expectancy >= 0.2:
            score += 15
        elif expectancy > 0:
            score += 10
        elif expectancy == 0:
            score += 5
        else:
            score += 0

    # Win Rate (0-15)
    if win_rate is not None:
        if win_rate >= 70:
            score += 15
        elif win_rate >= 60:
            score += 12
        elif win_rate >= 50:
            score += 9
        elif win_rate >= 40:
            score += 6
        else:
            score += 3

    # Max Drawdown (0-20)
    if max_drawdown_pct is not None:
        if max_drawdown_pct <= 5:
            score += 20
        elif max_drawdown_pct <= 10:
            score += 15
        elif max_drawdown_pct <= 15:
            score += 10
        elif max_drawdown_pct <= 20:
            score += 5
        else:
            score += 0

    # Ulcer Index (0-20)
    if ulcer_index is not None:
        if ulcer_index <= 2:
            score += 20
        elif ulcer_index <= 4:
            score += 15
        elif ulcer_index <= 6:
            score += 10
        elif ulcer_index <= 10:
            score += 5
        else:
            score += 0

    score = max(0, min(100, int(round(score))))

    if score >= 85:
        classification = "Elite Edge"
        summary = "Strong statistical edge with healthy risk structure."
    elif score >= 70:
        classification = "Strong Edge"
        summary = "Good edge profile with solid performance and controlled risk."
    elif score >= 55:
        classification = "Developing Edge"
        summary = "There are positive signals, but the edge still needs refinement."
    elif score >= 40:
        classification = "Fragile Edge"
        summary = "The edge is unstable and may be undermined by weak risk-reward structure."
    else:
        classification = "No Clear Edge"
        summary = "Current results do not yet show a strong and reliable statistical edge."

    return EdgeScoreResult(
        score=score,
        classification=classification,
        summary=summary,
    )