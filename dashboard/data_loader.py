from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from analytics.drawdown_series import build_drawdown_series_from_mt4_statement
from analytics.equity_builder import build_equity_timeline_from_mt4_statement
from analytics.importers import import_mt4_closed_trades
from analytics.normalizers import normalize_mt4_trades
from analytics.performance import PerformanceMetrics, calculate_performance_metrics
from analytics.service import calculate_account_metrics
from analytics.strategy_analyzer import StrategyAnalyzerResult, analyze_strategy_patterns
from analytics.streaks import TradeStreaks, calculate_trade_streaks
from analytics.trade_intelligence import TradeIntelligence, calculate_trade_intelligence
from analytics.trade_schema import DrawdownTimelinePoint, EquityTimelinePoint, NormalizedTrade
from analytics.types import AccountMetrics


DEFAULT_INITIAL_BALANCE = 1000.0
DEFAULT_CYCLE_TARGET_RATE = 0.05


@dataclass(frozen=True)
class DashboardData:
    normalized_trades: list[NormalizedTrade]
    performance: PerformanceMetrics
    streaks: TradeStreaks
    trade_intelligence: TradeIntelligence
    strategy_analyzer: StrategyAnalyzerResult
    account_metrics: AccountMetrics
    equity_timeline: list[EquityTimelinePoint]
    drawdown_series: list[DrawdownTimelinePoint]
    current_risk_zone: str
    current_drawdown_pct: float


def load_dashboard_data(
    statement_path: str | Path,
    initial_balance: float = DEFAULT_INITIAL_BALANCE,
    cycle_target: float | None = None,
) -> DashboardData:
    imported_trades = import_mt4_closed_trades(statement_path)
    normalized_trades = normalize_mt4_trades(imported_trades)
    pnl_values = [trade.net_profit for trade in normalized_trades]
    resolved_cycle_target = cycle_target if cycle_target is not None else _derive_cycle_target(initial_balance)

    performance = calculate_performance_metrics(normalized_trades)
    streaks = calculate_trade_streaks(normalized_trades)
    trade_intelligence = calculate_trade_intelligence(normalized_trades)
    strategy_analyzer = analyze_strategy_patterns(normalized_trades)
    account_metrics = calculate_account_metrics(
        initial_balance=initial_balance,
        pnl_values=pnl_values,
        cycle_target=resolved_cycle_target,
    )
    equity_timeline = build_equity_timeline_from_mt4_statement(
        path=statement_path,
        initial_balance=initial_balance,
    )
    drawdown_series = build_drawdown_series_from_mt4_statement(
        path=statement_path,
        initial_balance=initial_balance,
    )

    current_risk_zone = drawdown_series[-1].risk_zone if drawdown_series else "green"
    current_drawdown_pct = drawdown_series[-1].drawdown_pct if drawdown_series else 0.0

    return DashboardData(
        normalized_trades=normalized_trades,
        performance=performance,
        streaks=streaks,
        trade_intelligence=trade_intelligence,
        strategy_analyzer=strategy_analyzer,
        account_metrics=account_metrics,
        equity_timeline=equity_timeline,
        drawdown_series=drawdown_series,
        current_risk_zone=current_risk_zone,
        current_drawdown_pct=current_drawdown_pct,
    )


def _derive_cycle_target(initial_balance: float) -> float:
    return round(initial_balance * DEFAULT_CYCLE_TARGET_RATE, 2)
