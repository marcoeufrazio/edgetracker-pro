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
from analytics.recommendations.recommendation_engine import RecommendationEngine
from dashboard.components import get_dashboard_theme_css, render_metric_card, render_section_title
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE, load_dashboard_data
from dashboard.filters import TradeFilters, get_filter_options
from dashboard.insights_formatter import format_strategy_analyzer, format_trade_intelligence
from dashboard.recommendations_panel import render_recommendations_panel
from dashboard.strategy_panel import render_trade_intelligence_panel
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

    _section_spacing()

    render_section_title("Core Metrics", "Snapshot of the most important performance indicators.")
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

    render_section_title("Estado da Conta", "Core health and risk status for the current account.")

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

    render_section_title(
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

    render_section_title("Performance Charts", "Equity and drawdown curves for the current account.")
    chart_columns = st.columns(2)
    chart_columns[0].pyplot(create_equity_curve_chart(data.equity_timeline))
    chart_columns[1].pyplot(create_drawdown_curve_chart(data.drawdown_series))

    _section_spacing()

    render_trade_intelligence_panel(format_trade_intelligence(data.trade_intelligence))

    _section_spacing()

    formatted_strategy = format_strategy_analyzer(data.strategy_analyzer)
    _render_strategy_analyzer_cards(formatted_strategy)

    _section_spacing()

    render_section_title("Trade Explorer", f"{len(filtered_trade_rows)} filtered trades")
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
            margin-bottom: 1.25rem;
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


def _render_strategy_analyzer_cards(formatted_strategy: Any) -> None:
    render_section_title("Strategy Analyzer", "Execution behaviour, duration quality and streak resilience.")

    avg_duration = _extract_value(
        formatted_strategy,
        ["average_trade_duration", "avg_trade_duration"],
        default="-",
    )
    best_duration = _extract_value(
        formatted_strategy,
        ["best_duration_bucket"],
        default="-",
    )
    worst_duration = _extract_value(
        formatted_strategy,
        ["worst_duration_bucket"],
        default="-",
    )
    best_size = _extract_value(
        formatted_strategy,
        ["best_size_bucket"],
        default="-",
    )
    worst_size = _extract_value(
        formatted_strategy,
        ["worst_size_bucket"],
        default="-",
    )
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
    best_loss_recovery = _extract_value(
        formatted_strategy,
        ["best_recovery_after_loss_streak"],
        default="-",
    )
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

    return table, pnl_raw


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