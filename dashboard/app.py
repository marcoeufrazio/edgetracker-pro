from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from analytics.charts import create_drawdown_curve_chart, create_equity_curve_chart
from analytics.edge_score import calculate_edge_score
from analytics.recommendations.recommendation_engine import RecommendationEngine
from dashboard.components import render_metric_card
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE, load_dashboard_data
from dashboard.filters import TradeFilters, get_filter_options
from dashboard.insights_formatter import format_strategy_analyzer, format_trade_intelligence
from dashboard.recommendations_panel import render_recommendations_panel
from dashboard.sections.advanced_sections import (
    render_ai_strategy_coach,
    render_distribution_charts,
    render_equity_intelligence,
    render_risk_behaviour_analyzer,
    render_session_analyzer,
)
from dashboard.sections.comparison_sections import (
    load_comparison_accounts,
    render_multi_account_comparison,
    render_multi_account_selector,
)
from dashboard.sections.core_sections import (
    render_account_status,
    render_core_metrics,
    render_edge_score_banner,
    render_health_banner,
)
from dashboard.sections.insights_sections import (
    render_strategy_analyzer_cards,
    render_trade_intelligence_cards,
)
from dashboard.sections.report_sections import render_client_report_export
from dashboard.trade_explorer import build_filtered_trade_rows
from dashboard.trade_table_formatter import format_trade_table_for_display
from dashboard.utils import (
    drawdown_tone,
    inject_dashboard_styles,
    list_available_statements,
    parse_cycle_target,
    profit_tone,
    render_premium_section_header,
    resolve_selected_dates,
    safe_index,
    save_uploaded_statement,
    section_spacing,
    status_tone,
)


def main() -> None:
    st.set_page_config(page_title="EdgeTracker-Pro", layout="wide")
    inject_dashboard_styles()

    st.title("EdgeTracker-Pro Dashboard")
    st.caption("Professional trading analytics platform for performance, risk and edge discovery.")

    default_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    _initialize_general_inputs(default_path)

    available_statements = list_available_statements(PROJECT_ROOT)
    st.session_state.setdefault("comparison_statement_paths", [])

    with st.sidebar:
        st.markdown("### Sidebar")
        st.caption("Configure the statement source and explore filtered trades.")
        st.divider()
        _render_general_inputs_section(available_statements)
        section_spacing()
        comparison_statement_paths = render_multi_account_selector(
            PROJECT_ROOT,
            available_statements,
            st.session_state.statement_path,
        )

    cycle_target = parse_cycle_target(st.session_state.cycle_target_value)

    data = load_dashboard_data(
        st.session_state.statement_path,
        initial_balance=st.session_state.initial_balance,
        cycle_target=cycle_target,
    )

    comparison_results = load_comparison_accounts(
        current_statement_path=st.session_state.statement_path,
        comparison_statement_paths=comparison_statement_paths,
        initial_balance=st.session_state.initial_balance,
        cycle_target=cycle_target,
    )

    recommendation_metrics = {
        "profit_factor": data.performance.profit_factor,
        "win_rate": data.performance.win_rate,
        "max_drawdown": data.account_metrics.max_drawdown_pct,
        "best_symbol": getattr(data.trade_intelligence, "best_symbol", None),
        "worst_day": getattr(data.trade_intelligence, "worst_day", None),
        "expectancy": data.performance.expectancy,
        "health_score": getattr(data.account_metrics, "health_score", None),
        "health_classification": getattr(data.account_metrics, "health_classification", None),
        "best_hour": getattr(data.trade_intelligence, "best_hour", None),
        "worst_hour": getattr(data.trade_intelligence, "worst_hour", None),
        "best_duration_bucket": getattr(data.strategy_analyzer, "best_duration_bucket", None),
        "worst_duration_bucket": getattr(data.strategy_analyzer, "worst_duration_bucket", None),
    }

    engine = RecommendationEngine()
    recommendations = engine.generate(recommendation_metrics)

    edge_score = calculate_edge_score(
        profit_factor=data.performance.profit_factor,
        expectancy=data.performance.expectancy,
        win_rate=data.performance.win_rate,
        max_drawdown_pct=data.account_metrics.max_drawdown_pct,
        ulcer_index=data.account_metrics.ulcer_index,
    )

    filter_options = get_filter_options(data.normalized_trades)
    _initialize_trade_filters(data.normalized_trades)

    with st.sidebar:
        section_spacing()
        _render_trade_filters_section(filter_options, data.normalized_trades)

    date_from, date_to = resolve_selected_dates(st.session_state.filter_date_range)
    trade_filters = TradeFilters(
        symbol=st.session_state.filter_symbol,
        result_type=st.session_state.filter_result_type,
        day_of_week=st.session_state.filter_day_of_week,
        hour_of_day=st.session_state.filter_hour_of_day,
        date_from=date_from,
        date_to=date_to,
    )
    filtered_trade_rows = build_filtered_trade_rows(data.normalized_trades, trade_filters)

    render_health_banner(data, recommendations)
    render_edge_score_banner(edge_score)

    section_spacing()

    render_premium_section_header(
        "Core Metrics",
        "Snapshot of the most important performance indicators.",
    )
    render_core_metrics(data, profit_tone)

    section_spacing()

    render_premium_section_header(
        "Account Status",
        "Core health and risk status for the current account.",
    )
    render_account_status(data, status_tone, profit_tone, drawdown_tone)

    section_spacing()

    render_premium_section_header(
        "Key Recommendations",
        "Actionable insights generated from your current performance profile.",
    )
    _render_recommendation_summary(recommendations)
    render_recommendations_panel(recommendations)

    section_spacing()

    render_premium_section_header(
        "Performance Charts",
        "Equity and drawdown curves for the current account.",
    )
    chart_columns = st.columns(2)
    chart_columns[0].pyplot(create_equity_curve_chart(data.equity_timeline))
    chart_columns[1].pyplot(create_drawdown_curve_chart(data.drawdown_series))

    section_spacing()

    render_premium_section_header(
        "Trade Intelligence",
        "Best and worst timing, day and symbol behaviours extracted from your trades.",
    )
    formatted_trade_intelligence = format_trade_intelligence(data.trade_intelligence)
    render_trade_intelligence_cards(formatted_trade_intelligence)

    section_spacing()

    render_premium_section_header(
        "Strategy Analyzer",
        "Execution behaviour, duration quality and streak resilience.",
    )
    formatted_strategy = format_strategy_analyzer(data.strategy_analyzer)
    render_strategy_analyzer_cards(formatted_strategy, data.strategy_analyzer)

    section_spacing()

    render_premium_section_header(
        "Equity Intelligence & Streak Analyzer",
        "Daily equity behaviour, streak quality, recovery speed and momentum analysis.",
    )
    render_equity_intelligence(data.normalized_trades)

    section_spacing()

    render_premium_section_header(
        "Risk Behaviour Analyzer",
        "Detect overtrading, revenge behaviour, size escalation and post-loss pressure.",
    )
    render_risk_behaviour_analyzer(data.normalized_trades)

    section_spacing()

    render_premium_section_header(
        "AI Strategy Coach",
        "Action-oriented coaching generated from your edge, risk and behaviour profile.",
    )
    render_ai_strategy_coach(
        data=data,
        edge_score=edge_score,
        formatted_trade_intelligence=formatted_trade_intelligence,
        formatted_strategy=formatted_strategy,
    )

    section_spacing()

    render_premium_section_header(
        "Session Analyzer",
        "Performance segmented by Asia, London and New York trading sessions.",
    )
    render_session_analyzer(data.normalized_trades)

    section_spacing()

    render_premium_section_header(
        "Trade Distribution Charts",
        "Trade frequency and performance distribution across day, hour, symbol and result.",
    )
    render_distribution_charts(data.normalized_trades)

    section_spacing()

    render_premium_section_header(
        "Multi-Account Comparison",
        "Compare multiple statements side by side by profitability, risk and edge quality.",
    )
    comparison_df = render_multi_account_comparison(
        current_statement_path=st.session_state.statement_path,
        current_data=data,
        current_edge_score=edge_score,
        comparison_results=comparison_results,
    )

    section_spacing()

    render_premium_section_header(
        "Client Report Export",
        "Generate a clean deliverable report for clients, reviews or account audits.",
    )
    render_client_report_export(
        current_statement_path=st.session_state.statement_path,
        data=data,
        edge_score=edge_score,
        recommendations=recommendations,
        formatted_trade_intelligence=formatted_trade_intelligence,
        formatted_strategy=formatted_strategy,
        comparison_df=comparison_df,
    )

    section_spacing()

    render_premium_section_header(
        "Trade Explorer",
        f"{len(filtered_trade_rows)} filtered trades",
    )
    st.caption("Review execution quality, duration and result distribution trade by trade.")

    trade_table = pd.DataFrame(filtered_trade_rows)

    if not trade_table.empty:
        display_table, pnl_raw = format_trade_table_for_display(trade_table)

        def highlight_pnl(row):
            pnl_value = pnl_raw.loc[row.name] if row.name in pnl_raw.index else None
            if pd.isna(pnl_value):
                return [""] * len(row)
            if pnl_value > 0:
                return ["background-color: rgba(34, 197, 94, 0.10);"] * len(row)
            if pnl_value < 0:
                return ["background-color: rgba(239, 68, 68, 0.10);"] * len(row)
            return [""] * len(row)

        styled_table = display_table.style.apply(highlight_pnl, axis=1)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
    else:
        st.info("No trades match the current filters.")


def _initialize_general_inputs(default_path: Path) -> None:
    defaults = {
        "statement_path": str(default_path),
        "initial_balance": float(DEFAULT_INITIAL_BALANCE),
        "cycle_target_value": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _initialize_trade_filters(trades) -> None:
    close_dates = [trade.closed_at.date() for trade in trades]
    default_date_range = (min(close_dates), max(close_dates)) if close_dates else ()
    defaults = {
        "filter_symbol": "all",
        "filter_result_type": "all",
        "filter_day_of_week": "all",
        "filter_hour_of_day": "all",
        "filter_date_range": default_date_range,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _render_general_inputs_section(available_statements: list[str]) -> None:
    with st.container(border=True):
        st.markdown("#### Inputs Gerais")
        st.caption("Statement base e parametros principais do dashboard.")

        uploaded_file = st.file_uploader(
            "Upload MT4 Statement",
            type=["html", "htm"],
            help="Upload a detailed MT4 HTML report. The dashboard will automatically use it.",
        )

        if uploaded_file is not None:
            saved_path = save_uploaded_statement(PROJECT_ROOT, uploaded_file)
            st.session_state.statement_path = str(saved_path)
            st.success(f"Statement uploaded: {uploaded_file.name}")

        if available_statements:
            st.selectbox(
                "Available Statements",
                options=available_statements,
                index=safe_index(available_statements, st.session_state.statement_path),
                key="statement_path",
            )
        else:
            st.text_input("MT4 Statement", key="statement_path")

        st.number_input("Initial Balance", min_value=0.0, step=100.0, key="initial_balance")
        st.text_input("Cycle Target (optional)", key="cycle_target_value")


def _render_trade_filters_section(filter_options: dict[str, list[object]], trades) -> None:
    close_dates = [trade.closed_at.date() for trade in trades]
    default_date_range = (min(close_dates), max(close_dates)) if close_dates else ()

    header_columns = st.columns([1, 1])
    header_columns[0].markdown("#### Trade Filters")
    if header_columns[1].button("Reset Filters", use_container_width=True, type="primary"):
        st.session_state.filter_symbol = "all"
        st.session_state.filter_result_type = "all"
        st.session_state.filter_day_of_week = "all"
        st.session_state.filter_hour_of_day = "all"
        st.session_state.filter_date_range = default_date_range
        st.rerun()

    st.caption("Refine the trade table without changing the analytics pipeline.")

    with st.container(border=True):
        st.selectbox("Symbol", filter_options["symbols"], key="filter_symbol")
        st.selectbox("Result Type", filter_options["result_types"], key="filter_result_type")
        st.selectbox("Day Of Week", filter_options["days_of_week"], key="filter_day_of_week")
        st.selectbox("Hour Of Day", filter_options["hours_of_day"], key="filter_hour_of_day")
        st.date_input("Date Range", key="filter_date_range")


def _render_recommendation_summary(recommendations: list[dict[str, Any]]) -> None:
    recommendation_summary_columns = st.columns(3)
    risk_alerts = len([r for r in recommendations if r.get("type") in {"risk", "risk_management"}])
    timing_insights = len([r for r in recommendations if r.get("type") == "timing"])
    performance_insights = len([r for r in recommendations if r.get("type") == "performance"])

    with recommendation_summary_columns[0]:
        render_metric_card("Total Signals", str(len(recommendations)), tone="neutral")
    with recommendation_summary_columns[1]:
        render_metric_card("Risk Alerts", str(risk_alerts), tone="danger" if risk_alerts else "neutral")
    with recommendation_summary_columns[2]:
        render_metric_card(
            "Performance Insights",
            str(performance_insights + timing_insights),
            tone="good" if (performance_insights + timing_insights) else "neutral",
        )


if __name__ == "__main__":
    main()