from __future__ import annotations

from analytics.report_builder import ReportBundle


def format_report_summary_markdown(bundle: ReportBundle) -> str:
    lines = [
        "# EdgeTracker-Pro Report Summary",
        "",
        f"Generated at: {bundle.generated_at}",
        "",
        "## Main Metrics",
        f"- Total trades: {bundle.metrics_summary['total_trades']}",
        f"- Win rate: {bundle.metrics_summary['win_rate']:.2f}%",
        f"- Profit factor: {bundle.metrics_summary['profit_factor']:.4f}",
        f"- Expectancy: {bundle.metrics_summary['expectancy']:.4f}",
        f"- Net profit: {bundle.metrics_summary['net_profit']:.2f}",
        "",
        "## Health",
        f"- Traffic light: {bundle.metrics_summary['traffic_light']}",
        f"- Risk zone: {bundle.metrics_summary['risk_zone']}",
        f"- Max drawdown %: {bundle.metrics_summary['max_drawdown_pct']:.2f}",
        f"- Ulcer index: {bundle.metrics_summary['ulcer_index']:.4f}",
        f"- Health score: {bundle.health_score.health_score}",
        f"- Health classification: {bundle.health_score.health_classification}",
        "",
        "## Health Diagnostic",
        bundle.health_diagnostic,
        "",
        "## Trade Intelligence",
        f"- Best day: {bundle.trade_intelligence.best_day_of_week}",
        f"- Worst day: {bundle.trade_intelligence.worst_day_of_week}",
        f"- Best hour: {bundle.trade_intelligence.best_trading_hour}",
        f"- Worst hour: {bundle.trade_intelligence.worst_trading_hour}",
        f"- Best symbol: {bundle.trade_intelligence.best_symbol}",
        f"- Worst symbol: {bundle.trade_intelligence.worst_symbol}",
        "",
        "## Strategy Analyzer",
        f"- Average trade duration: {bundle.strategy_analyzer.average_trade_duration_minutes:.2f} minutes",
        f"- Best duration bucket: {_format_best_worst(bundle.strategy_analyzer.performance_by_duration, 'best')}",
        f"- Worst duration bucket: {_format_best_worst(bundle.strategy_analyzer.performance_by_duration, 'worst')}",
        f"- Best size bucket: {_format_best_worst(bundle.strategy_analyzer.performance_by_position_size, 'best')}",
        f"- Worst size bucket: {_format_best_worst(bundle.strategy_analyzer.performance_by_position_size, 'worst')}",
        f"- Best continuation after win streak: {_format_best_worst(bundle.strategy_analyzer.performance_after_win_streak, 'best', 'wins')}",
        f"- Worst continuation after win streak: {_format_best_worst(bundle.strategy_analyzer.performance_after_win_streak, 'worst', 'wins')}",
        f"- Best recovery after loss streak: {_format_best_worst(bundle.strategy_analyzer.performance_after_loss_streak, 'best', 'losses')}",
        f"- Worst continuation after loss streak: {_format_best_worst(bundle.strategy_analyzer.performance_after_loss_streak, 'worst', 'losses')}",
    ]

    return "\n".join(lines)


def _format_best_worst(values: dict[object, float], mode: str, suffix: str = "") -> str:
    if not values:
        return "Not available"

    key = max(values, key=values.get) if mode == "best" else min(values, key=values.get)
    label = f"{key} {suffix}".strip()
    return f"{label} ({values[key]:.4f})"
