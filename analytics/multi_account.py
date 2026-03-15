from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from analytics.health_score import calculate_health_score
from analytics.importers import load_mt4_statement_html
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE, DashboardData, load_dashboard_data


@dataclass(frozen=True)
class AccountAnalysis:
    account_id: str
    statement_path: str
    dashboard_data: DashboardData
    health_score: int
    health_classification: str


def analyze_multiple_accounts(
    statement_paths: list[str | Path],
    initial_balance: float = DEFAULT_INITIAL_BALANCE,
    cycle_target: float | None = None,
) -> list[AccountAnalysis]:
    analyses: list[AccountAnalysis] = []

    for statement_path in statement_paths:
        dashboard_data = load_dashboard_data(
            statement_path=statement_path,
            initial_balance=initial_balance,
            cycle_target=cycle_target,
        )
        health = calculate_health_score(
            profit_factor=dashboard_data.performance.profit_factor,
            expectancy=dashboard_data.performance.expectancy,
            max_drawdown_pct=dashboard_data.account_metrics.max_drawdown_pct,
            ulcer_index=dashboard_data.account_metrics.ulcer_index,
            risk_zone=dashboard_data.current_risk_zone,
            traffic_light=dashboard_data.account_metrics.traffic_light,
        )
        analyses.append(
            AccountAnalysis(
                account_id=_extract_account_id(statement_path),
                statement_path=str(statement_path),
                dashboard_data=dashboard_data,
                health_score=health.health_score,
                health_classification=health.health_classification,
            )
        )

    return analyses


def _extract_account_id(statement_path: str | Path) -> str:
    path = Path(statement_path)
    html = load_mt4_statement_html(path)
    match = re.search(r"Account:\s*([0-9]+)", html)
    if match is not None:
        return match.group(1)
    return path.stem
