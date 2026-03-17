from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from analytics.charts import create_drawdown_curve_chart, create_equity_curve_chart
from analytics.edge_score import calculate_edge_score
from analytics.recommendations.recommendation_engine import RecommendationEngine
from dashboard.components import get_dashboard_theme_css, render_metric_card
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE, load_dashboard_data
from dashboard.filters import TradeFilters, get_filter_options
from dashboard.insights_formatter import format_strategy_analyzer, format_trade_intelligence
from dashboard.recommendations_panel import render_recommendations_panel
from dashboard.trade_explorer import build_filtered_trade_rows


GENERAL_INPUT_KEYS = (
    "statement_path",
    "initial_balance",
    "cycle_target_value",
)
TRADE_FILTER_KEYS = (
    "filter_symbol",
    "filter_result_type",
    "filter_day_of_week",
    "filter_hour_of_day",
    "filter_date_range",
)


def main() -> None:
    st.set_page_config(page_title="EdgeTracker-Pro", layout="wide")
    _inject_dashboard_styles()

    st.title("EdgeTracker-Pro Dashboard")
    st.caption("Professional trading analytics platform for performance, risk and edge discovery.")

    default_path = PROJECT_ROOT / "data" / "imports" / "mt4_statement.html"
    _initialize_general_inputs(default_path)

    with st.sidebar:
        st.markdown("### Sidebar")
        st.caption("Configure the statement source and explore filtered trades.")
        st.divider()
        _render_general_inputs_section()

    cycle_target = _parse_cycle_target(st.session_state.cycle_target_value)

    data = load_dashboard_data(
        st.session_state.statement_path,
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
        _section_spacing()
        _render_trade_filters_section(filter_options, data.normalized_trades)

    date_from, date_to = _resolve_selected_dates(st.session_state.filter_date_range)
    trade_filters = TradeFilters(
        symbol=st.session_state.filter_symbol,
        result_type=st.session_state.filter_result_type,
        day_of_week=st.session_state.filter_day_of_week,
        hour_of_day=st.session_state.filter_hour_of_day,
        date_from=date_from,
        date_to=date_to,
    )
    filtered_trade_rows = build_filtered_trade_rows(data.normalized_trades, trade_filters)

    _render_health_banner(data, recommendations)
    _render_edge_score_banner(edge_score)

    _section_spacing()

    _render_premium_section_header(
        "Core Metrics",
        "Snapshot of the most important performance indicators.",
    )
    metric_columns = st.columns(5)
    with metric_columns[0]:
        render_metric_card("Total Trades", str(data.performance.total_trades))
    with metric_columns[1]:
        render_metric_card("Win Rate", f"{data.performance.win_rate:.2f}%", tone="good")
    with metric_columns[2]:
        render_metric_card("Profit Factor", f"{data.performance.profit_factor:.4f}")
    with metric_columns[3]:
        render_metric_card("Expectancy", f"{data.performance.expectancy:.4f}")
    with metric_columns[4]:
        render_metric_card(
            "Net Profit",
            f"{data.performance.net_profit:.2f}",
            tone=_profit_tone(data.performance.net_profit),
        )

    _section_spacing()

    _render_premium_section_header(
        "Account Status",
        "Core health and risk status for the current account.",
    )

    summary_columns = st.columns(3)
    with summary_columns[0]:
        render_metric_card(
            "Profit",
            f"{data.performance.net_profit:.2f}",
            tone=_profit_tone(data.performance.net_profit),
        )
    with summary_columns[1]:
        render_metric_card(
            "Max Drawdown",
            f"{data.account_metrics.max_drawdown_pct:.2f}%",
            tone=_drawdown_tone(data.account_metrics.max_drawdown_pct),
        )
    with summary_columns[2]:
        render_metric_card(
            "Ulcer Index",
            f"{data.account_metrics.ulcer_index:.2f}",
            tone="neutral",
        )

    state_columns = st.columns(3)
    with state_columns[0]:
        traffic_value = data.account_metrics.traffic_light.lower()
        traffic_label = {
            "green": "🟢 Green",
            "yellow": "🟡 Yellow",
            "red": "🔴 Red",
        }.get(traffic_value, traffic_value.title())

        render_metric_card(
            "Traffic Light",
            traffic_label,
            tone=_status_tone(traffic_value),
        )

    with state_columns[1]:
        risk_value = data.current_risk_zone.lower()
        risk_label = {
            "green": "🟢 Green",
            "yellow": "🟡 Yellow",
            "red": "🔴 Red",
        }.get(risk_value, risk_value.title())

        render_metric_card(
            "Risk Zone",
            risk_label,
            tone=_status_tone(risk_value),
        )

    with state_columns[2]:
        render_metric_card(
            "Current Drawdown %",
            f"{data.current_drawdown_pct:.2f}%",
            tone=_drawdown_tone(data.current_drawdown_pct),
        )

    _section_spacing()

    _render_premium_section_header(
        "Key Recommendations",
        "Actionable insights generated from your current performance profile.",
    )

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

    render_recommendations_panel(recommendations)

    _section_spacing()

    _render_premium_section_header(
        "Performance Charts",
        "Equity and drawdown curves for the current account.",
    )
    chart_columns = st.columns(2)
    chart_columns[0].pyplot(create_equity_curve_chart(data.equity_timeline))
    chart_columns[1].pyplot(create_drawdown_curve_chart(data.drawdown_series))

    _section_spacing()

    _render_premium_section_header(
        "Trade Intelligence",
        "Best and worst timing, day and symbol behaviours extracted from your trades.",
    )
    formatted_trade_intelligence = format_trade_intelligence(data.trade_intelligence)
    _render_trade_intelligence_cards(formatted_trade_intelligence)

    _section_spacing()

    formatted_strategy = format_strategy_analyzer(data.strategy_analyzer)
    _render_strategy_analyzer_cards(formatted_strategy)

    _section_spacing()

    _render_premium_section_header(
        "Equity Intelligence & Streak Analyzer",
        "Daily equity behaviour, streak quality, recovery speed and momentum analysis.",
    )
    _render_equity_intelligence(data.normalized_trades)

    _section_spacing()

    _render_premium_section_header(
        "Session Analyzer",
        "Performance segmented by Asia, London and New York trading sessions.",
    )
    _render_session_analyzer(data.normalized_trades)

    _section_spacing()

    _render_premium_section_header(
        "Trade Distribution Charts",
        "Trade frequency and performance distribution across day, hour, symbol and result.",
    )
    _render_distribution_charts(data.normalized_trades)

    _section_spacing()

    _render_premium_section_header(
        "Trade Explorer",
        f"{len(filtered_trade_rows)} filtered trades",
    )
    st.caption("Review execution quality, duration and result distribution trade by trade.")

    trade_table = pd.DataFrame(filtered_trade_rows)

    if not trade_table.empty:
        display_table, pnl_raw = _format_trade_table(trade_table)

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

        st.dataframe(
            styled_table,
            use_container_width=True,
            hide_index=True,
        )
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


def _render_general_inputs_section() -> None:
    with st.container(border=True):
        st.markdown("#### Inputs Gerais")
        st.caption("Statement base e parametros principais do dashboard.")

        uploaded_file = st.file_uploader(
            "Upload MT4 Statement",
            type=["html", "htm"],
            help="Upload a detailed MT4 HTML report. The dashboard will automatically use it.",
        )

        if uploaded_file is not None:
            saved_path = _save_uploaded_statement(uploaded_file)
            st.session_state.statement_path = str(saved_path)
            st.success(f"Statement uploaded: {uploaded_file.name}")

        st.text_input("MT4 Statement", key="statement_path")
        st.number_input("Initial Balance", min_value=0.0, step=100.0, key="initial_balance")
        st.text_input("Cycle Target (optional)", key="cycle_target_value")


def _render_trade_filters_section(filter_options: dict[str, list[object]], trades) -> None:
    close_dates = [trade.closed_at.date() for trade in trades]
    default_date_range = (min(close_dates), max(close_dates)) if close_dates else ()

    header_columns = st.columns([1, 1])
    header_columns[0].markdown("#### Trade Filters")
    if header_columns[1].button("Reset Filters", use_container_width=True, type="primary"):
        _reset_trade_filters(default_date_range)
        st.rerun()

    st.caption("Refine the trade table without changing the analytics pipeline.")

    with st.container(border=True):
        st.selectbox("Symbol", filter_options["symbols"], key="filter_symbol")
        st.selectbox("Result Type", filter_options["result_types"], key="filter_result_type")
        st.selectbox("Day Of Week", filter_options["days_of_week"], key="filter_day_of_week")
        st.selectbox("Hour Of Day", filter_options["hours_of_day"], key="filter_hour_of_day")
        st.date_input("Date Range", key="filter_date_range")


def _reset_trade_filters(default_date_range) -> None:
    st.session_state.filter_symbol = "all"
    st.session_state.filter_result_type = "all"
    st.session_state.filter_day_of_week = "all"
    st.session_state.filter_hour_of_day = "all"
    st.session_state.filter_date_range = default_date_range


def _resolve_selected_dates(selected_dates):
    if isinstance(selected_dates, tuple):
        return selected_dates[0], selected_dates[1]
    return selected_dates, selected_dates


def _parse_cycle_target(value: str) -> float | None:
    return float(value) if value.strip() else None


def _inject_dashboard_styles() -> None:
    st.markdown(get_dashboard_theme_css(), unsafe_allow_html=True)


def _section_spacing() -> None:
    st.markdown("<div style='margin: 1.25rem 0;'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)


def _render_premium_section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div style="
            margin-top: 0.2rem;
            margin-bottom: 1rem;
            padding: 1rem 1.25rem;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(15,23,42,0.92));
        ">
            <div style="font-size: 1.35rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.35rem;">
                {title}
            </div>
            <div style="font-size: 0.95rem; color: #cbd5e1;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _status_tone(value: str) -> str:
    mapping = {"green": "good", "yellow": "warning", "red": "danger"}
    return mapping.get(value.lower(), "neutral")


def _profit_tone(value: float) -> str:
    if value > 0:
        return "good"
    if value < 0:
        return "danger"
    return "neutral"


def _drawdown_tone(value: float) -> str:
    if value <= 5:
        return "good"
    if value <= 10:
        return "warning"
    return "danger"


def _save_uploaded_statement(uploaded_file) -> Path:
    uploads_dir = PROJECT_ROOT / "data" / "imports"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(uploaded_file.name).name
    saved_path = uploads_dir / safe_name
    saved_path.write_bytes(uploaded_file.getbuffer())

    return saved_path


def _render_health_banner(data: Any, recommendations: list[dict[str, Any]]) -> None:
    traffic_value = data.account_metrics.traffic_light.lower()
    risk_value = data.current_risk_zone.lower()
    banner_color = {
        "green": "#14532d",
        "yellow": "#713f12",
        "red": "#7f1d1d",
    }.get(traffic_value, "#1f2937")

    traffic_label = traffic_value.title()
    risk_label = risk_value.title()
    signal_count = len(recommendations)

    st.markdown(
        f"""
        <div style="
            margin-top: 0.5rem;
            margin-bottom: 1.0rem;
            padding: 1rem 1.25rem;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(135deg, {banner_color}22, rgba(15,23,42,0.92));
        ">
            <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.35rem;">ACCOUNT HEALTH BANNER</div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.5rem;">
                Traffic Light: {traffic_label} · Risk Zone: {risk_label}
            </div>
            <div style="font-size: 0.95rem; color: #cbd5e1;">
                Net Profit {data.performance.net_profit:.2f} · Max Drawdown {data.account_metrics.max_drawdown_pct:.2f}% ·
                Ulcer Index {data.account_metrics.ulcer_index:.2f} · Recommendation Signals {signal_count}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_edge_score_banner(edge_score) -> None:
    if edge_score.score >= 70:
        tone_color = "#14532d"
        score_label = "🟢 Strong"
        badge_bg = "rgba(34, 197, 94, 0.18)"
    elif edge_score.score >= 55:
        tone_color = "#713f12"
        score_label = "🟡 Moderate"
        badge_bg = "rgba(245, 158, 11, 0.18)"
    else:
        tone_color = "#7f1d1d"
        score_label = "🔴 Weak"
        badge_bg = "rgba(239, 68, 68, 0.18)"

    st.markdown(
        f"""
        <div style="
            margin-top: 0.25rem;
            margin-bottom: 1.25rem;
            padding: 1rem 1.25rem;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(135deg, {tone_color}22, rgba(15,23,42,0.92));
        ">
            <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.35rem;">EDGE SCORE</div>
            <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.5rem;">
                <div style="font-size: 1.75rem; font-weight: 800; color: #f8fafc;">
                    {edge_score.score} / 100
                </div>
                <div style="
                    padding: 0.3rem 0.65rem;
                    border-radius: 999px;
                    background: {badge_bg};
                    color: #e5e7eb;
                    font-size: 0.9rem;
                    font-weight: 700;
                ">
                    {score_label}
                </div>
            </div>
            <div style="font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.25rem;">
                {edge_score.classification}
            </div>
            <div style="font-size: 0.95rem; color: #cbd5e1;">
                {edge_score.summary}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_trade_intelligence_cards(trade_intelligence: Any) -> None:
    def pick(*keys, default="-"):
        if isinstance(trade_intelligence, dict):
            for key in keys:
                value = trade_intelligence.get(key)
                if value not in (None, "", []):
                    return value
            return default

        for key in keys:
            value = getattr(trade_intelligence, key, None)
            if value not in (None, "", []):
                return value

        return default

    best_day = pick("best_day", "best_day_of_week")
    worst_day = pick("worst_day", "worst_day_of_week")
    best_hour = pick("best_hour", "best_trading_hour")
    worst_hour = pick("worst_hour", "worst_trading_hour")
    best_symbol = pick("best_symbol")
    worst_symbol = pick("worst_symbol")

    if isinstance(best_hour, (int, float)) or str(best_hour).isdigit():
        best_hour = f"{int(best_hour)}:00"
    if isinstance(worst_hour, (int, float)) or str(worst_hour).isdigit():
        worst_hour = f"{int(worst_hour)}:00"

    row1 = st.columns(3)
    with row1[0]:
        render_metric_card("Best Day", str(best_day), tone="good")
    with row1[1]:
        render_metric_card("Worst Day", str(worst_day), tone="danger")
    with row1[2]:
        render_metric_card("Best Hour", str(best_hour), tone="good")

    row2 = st.columns(3)
    with row2[0]:
        render_metric_card("Worst Hour", str(worst_hour), tone="danger")
    with row2[1]:
        render_metric_card("Best Symbol", str(best_symbol), tone="good")
    with row2[2]:
        render_metric_card("Worst Symbol", str(worst_symbol), tone="danger")


def _render_strategy_analyzer_cards(formatted_strategy: Any) -> None:
    _render_premium_section_header(
        "Strategy Analyzer",
        "Execution behaviour, duration quality and streak resilience.",
    )

    avg_duration = _extract_value(formatted_strategy, ["average_trade_duration", "avg_trade_duration"], default="-")
    best_duration = _extract_value(formatted_strategy, ["best_duration_bucket"], default="-")
    worst_duration = _extract_value(formatted_strategy, ["worst_duration_bucket"], default="-")
    best_size = _extract_value(formatted_strategy, ["best_size_bucket"], default="-")
    worst_size = _extract_value(formatted_strategy, ["worst_size_bucket"], default="-")
    best_win_cont = _extract_value(
        formatted_strategy,
        ["best_continuation_after_win_streak", "best_win_streak_continuation"],
        default="-",
    )
    worst_win_cont = _extract_value(
        formatted_strategy,
        ["worst_continuation_after_win_streak", "worst_win_streak_continuation"],
        default="-",
    )
    best_loss_recovery = _extract_value(formatted_strategy, ["best_recovery_after_loss_streak"], default="-")
    worst_loss_cont = _extract_value(
        formatted_strategy,
        ["worst_continuation_after_loss_streak", "worst_loss_streak_continuation"],
        default="-",
    )

    row1 = st.columns(3)
    with row1[0]:
        render_metric_card("Average Trade Duration", str(avg_duration), tone="neutral")
    with row1[1]:
        render_metric_card("Best Duration Bucket", str(best_duration), tone="good")
    with row1[2]:
        render_metric_card("Worst Duration Bucket", str(worst_duration), tone="danger")

    row2 = st.columns(3)
    with row2[0]:
        render_metric_card("Best Size Bucket", str(best_size), tone="good")
    with row2[1]:
        render_metric_card("Worst Size Bucket", str(worst_size), tone="danger")
    with row2[2]:
        render_metric_card("Best Win-Streak Continuation", str(best_win_cont), tone="good")

    row3 = st.columns(3)
    with row3[0]:
        render_metric_card("Worst Win-Streak Continuation", str(worst_win_cont), tone="danger")
    with row3[1]:
        render_metric_card("Best Loss Recovery", str(best_loss_recovery), tone="good")
    with row3[2]:
        render_metric_card("Worst Loss Continuation", str(worst_loss_cont), tone="danger")


def _render_equity_intelligence(trades: list[Any]) -> None:
    if not trades:
        st.info("No trades available for equity intelligence.")
        return

    rows = []
    ordered_trades = sorted(
        [trade for trade in trades if getattr(trade, "closed_at", None) is not None],
        key=lambda x: x.closed_at,
    )

    for trade in ordered_trades:
        closed_at = getattr(trade, "closed_at", None)
        pnl = getattr(trade, "net_profit", None)
        if closed_at is None or pnl is None:
            continue
        rows.append({"date": closed_at.date(), "pnl": float(pnl)})

    if not rows:
        st.info("No trades available for equity intelligence.")
        return

    df = pd.DataFrame(rows)
    daily_pnl = df.groupby("date")["pnl"].sum().sort_index()

    best_day = daily_pnl.idxmax()
    worst_day = daily_pnl.idxmin()
    best_day_pnl = daily_pnl.max()
    worst_day_pnl = daily_pnl.min()

    longest_win_streak = 0
    longest_loss_streak = 0
    current_streak_len = 0
    current_streak_type = "Neutral"

    current_win_streak = 0
    current_loss_streak = 0

    for _, row in df.iterrows():
        pnl = row["pnl"]

        if pnl > 0:
            current_win_streak += 1
            current_loss_streak = 0
            longest_win_streak = max(longest_win_streak, current_win_streak)
        elif pnl < 0:
            current_loss_streak += 1
            current_win_streak = 0
            longest_loss_streak = max(longest_loss_streak, current_loss_streak)
        else:
            current_win_streak = 0
            current_loss_streak = 0

    streak_state = []
    for _, row in df.iterrows():
        pnl = row["pnl"]
        if pnl > 0:
            streak_state.append("W")
        elif pnl < 0:
            streak_state.append("L")
        else:
            streak_state.append("B")

    if streak_state:
        last = streak_state[-1]
        if last == "W":
            current_streak_type = "Winning"
            current_streak_len = 1
            for value in reversed(streak_state[:-1]):
                if value == "W":
                    current_streak_len += 1
                else:
                    break
        elif last == "L":
            current_streak_type = "Losing"
            current_streak_len = 1
            for value in reversed(streak_state[:-1]):
                if value == "L":
                    current_streak_len += 1
                else:
                    break
        else:
            current_streak_type = "Breakeven"
            current_streak_len = 1

    recovery_lengths = []
    i = 0
    pnl_values = df["pnl"].tolist()
    while i < len(pnl_values):
        if pnl_values[i] < 0:
            j = i + 1
            steps = 0
            while j < len(pnl_values):
                steps += 1
                if pnl_values[j] > 0:
                    recovery_lengths.append(steps)
                    break
                j += 1
            i = j
        else:
            i += 1

    avg_recovery = sum(recovery_lengths) / len(recovery_lengths) if recovery_lengths else 0.0

    if current_streak_type == "Winning" and current_streak_len >= 3:
        hot_streak = f"🔥 {current_streak_len}-trade winning streak"
        hot_tone = "good"
    elif current_streak_type == "Losing" and current_streak_len >= 3:
        hot_streak = f"⚠️ {current_streak_len}-trade losing streak"
        hot_tone = "danger"
    else:
        hot_streak = "Stable / no extreme streak"
        hot_tone = "neutral"

    row1 = st.columns(4)
    with row1[0]:
        render_metric_card("Best Equity Day", str(best_day), tone="good")
    with row1[1]:
        render_metric_card("Worst Equity Day", str(worst_day), tone="danger")
    with row1[2]:
        render_metric_card("Best Day PnL", f"{best_day_pnl:.2f}", tone="good")
    with row1[3]:
        render_metric_card("Worst Day PnL", f"{worst_day_pnl:.2f}", tone="danger")

    row2 = st.columns(4)
    with row2[0]:
        render_metric_card("Longest Win Streak", str(longest_win_streak), tone="good")
    with row2[1]:
        render_metric_card("Longest Loss Streak", str(longest_loss_streak), tone="danger")
    with row2[2]:
        render_metric_card("Current Streak", f"{current_streak_type} ({current_streak_len})", tone="neutral")
    with row2[3]:
        render_metric_card("Recovery Speed", f"{avg_recovery:.1f} trades", tone="neutral")

    row3 = st.columns(1)
    with row3[0]:
        render_metric_card("Hot Streak Detection", hot_streak, tone=hot_tone)


def _render_session_analyzer(trades: list[Any]) -> None:
    session_stats = {"Asia": [], "London": [], "New York": []}

    for trade in trades:
        closed_at = getattr(trade, "closed_at", None)
        pnl = getattr(trade, "net_profit", None)
        if closed_at is None or pnl is None:
            continue

        hour = closed_at.hour
        if 0 <= hour < 8:
            session_stats["Asia"].append(float(pnl))
        elif 8 <= hour < 16:
            session_stats["London"].append(float(pnl))
        else:
            session_stats["New York"].append(float(pnl))

    columns = st.columns(3)
    for idx, session_name in enumerate(["Asia", "London", "New York"]):
        values = session_stats[session_name]
        total_trades = len(values)
        total_pnl = sum(values) if values else 0.0
        avg_pnl = (total_pnl / total_trades) if total_trades else 0.0
        win_rate = (sum(1 for v in values if v > 0) / total_trades * 100) if total_trades else 0.0

        tone = "neutral"
        if total_pnl > 0:
            tone = "good"
        elif total_pnl < 0:
            tone = "danger"

        with columns[idx]:
            render_metric_card(session_name, f"{total_pnl:.2f}", tone=tone)
            st.caption(f"Trades: {total_trades} · Win Rate: {win_rate:.1f}% · Avg PnL: {avg_pnl:.2f}")


def _render_distribution_charts(trades: list[Any]) -> None:
    if not trades:
        st.info("No trades available for distribution analysis.")
        return

    rows = []
    for trade in trades:
        closed_at = getattr(trade, "closed_at", None)
        pnl = getattr(trade, "net_profit", None)
        symbol = getattr(trade, "symbol", None)

        if closed_at is None or pnl is None:
            continue

        rows.append(
            {
                "day": closed_at.strftime("%A"),
                "hour": closed_at.hour,
                "symbol": symbol,
                "result": "Win" if pnl > 0 else "Loss" if pnl < 0 else "Breakeven",
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No trades available for distribution analysis.")
        return

    chart_cols_1 = st.columns(2)
    chart_cols_2 = st.columns(2)

    with chart_cols_1[0]:
        st.markdown("**Trades by Day**")
        fig = _simple_bar_chart(
            df["day"].value_counts().reindex(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                fill_value=0,
            ),
            xlabel="Day",
            ylabel="Trades",
        )
        st.pyplot(fig)

    with chart_cols_1[1]:
        st.markdown("**Trades by Hour**")
        fig = _simple_bar_chart(
            df["hour"].value_counts().sort_index(),
            xlabel="Hour",
            ylabel="Trades",
        )
        st.pyplot(fig)

    with chart_cols_2[0]:
        st.markdown("**Trades by Symbol**")
        fig = _simple_bar_chart(
            df["symbol"].value_counts().head(8),
            xlabel="Symbol",
            ylabel="Trades",
        )
        st.pyplot(fig)

    with chart_cols_2[1]:
        st.markdown("**Trades by Result**")
        fig = _simple_bar_chart(
            df["result"].value_counts(),
            xlabel="Result",
            ylabel="Trades",
        )
        st.pyplot(fig)


def _simple_bar_chart(series: pd.Series, xlabel: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    series.plot(kind="bar", ax=ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return fig


def _extract_value(source: Any, keys: list[str], default: str = "-") -> Any:
    if isinstance(source, dict):
        for key in keys:
            if key in source and source[key] not in (None, ""):
                return source[key]
        return default

    for key in keys:
        value = getattr(source, key, None)
        if value not in (None, ""):
            return value

    return default


def _format_trade_table(trade_table: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    table = trade_table.copy()

    rename_map = {
        "ticket": "Ticket",
        "symbol": "Symbol",
        "type": "Type",
        "open_time": "Open Time",
        "close_time": "Close Time",
        "pnl": "PnL",
        "volume": "Volume",
        "duration_minutes": "Duration",
        "r_multiple": "R Multiple",
    }
    table = table.rename(columns=rename_map)

    pnl_raw = table["PnL"].copy() if "PnL" in table.columns else pd.Series(index=table.index, dtype=float)

    if "PnL" in table.columns:
        table["PnL"] = table["PnL"].map(_format_pnl)

    if "Volume" in table.columns:
        table["Volume"] = table["Volume"].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

    if "Duration" in table.columns:
        table["Duration"] = table["Duration"].map(_format_duration)

    if "R Multiple" in table.columns:
        table["R Multiple"] = table["R Multiple"].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

    if "Type" in table.columns:
        table["Type"] = table["Type"].map(_format_trade_type)

    if "Symbol" in table.columns:
        table["Symbol"] = table["Symbol"].map(_format_symbol_badge)

    display_columns = [
        "Ticket",
        "Symbol",
        "Type",
        "Open Time",
        "Close Time",
        "PnL",
        "Volume",
        "Duration",
    ]

    if "R Multiple" in table.columns:
        display_columns.append("R Multiple")

    return table[display_columns], pnl_raw


def _format_pnl(value) -> str:
    if pd.isna(value):
        return ""

    if value > 0:
        return f"🟢 +{value:.2f}"
    if value < 0:
        return f"🔴 {value:.2f}"
    return f"{value:.2f}"


def _format_duration(minutes) -> str:
    if pd.isna(minutes):
        return ""

    total_seconds = int(round(float(minutes) * 60))
    m = total_seconds // 60
    s = total_seconds % 60
    return f"{m}:{s:02d}"


def _format_trade_type(value: str) -> str:
    if not value:
        return ""

    value_lower = str(value).lower()
    if value_lower == "buy":
        return "🟢 BUY"
    if value_lower == "sell":
        return "🔴 SELL"
    return str(value).upper()


def _format_symbol_badge(value: str) -> str:
    if not value:
        return ""

    symbol = str(value).upper()

    symbol_icons = {
        "EURUSD": "💶 EURUSD",
        "GBPUSD": "💷 GBPUSD",
        "USDJPY": "💴 USDJPY",
        "XAUUSD": "🥇 XAUUSD",
        "US30": "🇺🇸 US30",
        "NAS100": "💻 NAS100",
        "SPX500": "📊 SPX500",
    }

    return symbol_icons.get(symbol, f"🏷️ {symbol}")


if __name__ == "__main__":
    main()