from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path

from analytics.health_diagnostics import build_health_diagnostic_text
from analytics.health_score import HealthScoreResult, calculate_health_score
from analytics.strategy_analyzer import StrategyAnalyzerResult
from analytics.trade_intelligence import TradeIntelligence
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE, DashboardData, load_dashboard_data
from dashboard.trade_table import build_trade_table_rows


@dataclass(frozen=True)
class ReportBundle:
    generated_at: str
    metrics_summary: dict[str, object]
    trades_export_rows: list[dict[str, object]]
    trade_intelligence: TradeIntelligence
    strategy_analyzer: StrategyAnalyzerResult
    health_score: HealthScoreResult
    health_diagnostic: str


def build_report_bundle(
    statement_path: str | Path,
    initial_balance: float = DEFAULT_INITIAL_BALANCE,
    cycle_target: float | None = None,
) -> ReportBundle:
    dashboard_data = load_dashboard_data(
        statement_path=statement_path,
        initial_balance=initial_balance,
        cycle_target=cycle_target,
    )
    health_score = _build_health_score(dashboard_data)
    health_diagnostic = build_health_diagnostic_text(
        health_classification=health_score.health_classification,
        profit_factor=dashboard_data.performance.profit_factor,
        expectancy=dashboard_data.performance.expectancy,
        max_drawdown_pct=dashboard_data.account_metrics.max_drawdown_pct,
        ulcer_index=dashboard_data.account_metrics.ulcer_index,
        risk_zone=dashboard_data.current_risk_zone,
        traffic_light=dashboard_data.account_metrics.traffic_light,
    )

    return ReportBundle(
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        metrics_summary=_build_metrics_summary(dashboard_data, health_score),
        trades_export_rows=build_trade_table_rows(dashboard_data.normalized_trades),
        trade_intelligence=dashboard_data.trade_intelligence,
        strategy_analyzer=dashboard_data.strategy_analyzer,
        health_score=health_score,
        health_diagnostic=health_diagnostic,
    )


def _build_health_score(data: DashboardData) -> HealthScoreResult:
    return calculate_health_score(
        profit_factor=data.performance.profit_factor,
        expectancy=data.performance.expectancy,
        max_drawdown_pct=data.account_metrics.max_drawdown_pct,
        ulcer_index=data.account_metrics.ulcer_index,
        risk_zone=data.current_risk_zone,
        traffic_light=data.account_metrics.traffic_light,
    )


def _build_metrics_summary(data: DashboardData, health_score: HealthScoreResult) -> dict[str, object]:
    return {
        "total_trades": data.performance.total_trades,
        "win_rate": round(data.performance.win_rate, 2),
        "profit_factor": round(data.performance.profit_factor, 4),
        "expectancy": round(data.performance.expectancy, 4),
        "net_profit": round(data.performance.net_profit, 2),
        "traffic_light": data.account_metrics.traffic_light,
        "risk_zone": data.current_risk_zone,
        "max_drawdown_pct": round(data.account_metrics.max_drawdown_pct, 2),
        "ulcer_index": round(data.account_metrics.ulcer_index, 4),
        "health_score": health_score.health_score,
        "health_classification": health_score.health_classification,
    }
