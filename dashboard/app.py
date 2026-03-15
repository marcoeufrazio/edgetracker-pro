from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from analytics.charts import create_drawdown_curve_chart, create_equity_curve_chart
from dashboard.components import get_dashboard_theme_css, render_metric_card, render_section_title
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE, load_dashboard_data
from dashboard.filters import TradeFilters, get_filter_options
from dashboard.insights_formatter import format_strategy_analyzer, format_trade_intelligence
from dashboard.strategy_panel import render_strategy_analyzer_panel, render_trade_intelligence_panel
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
    st.caption("Professional trade analytics dashboard for equity, risk, performance, and insights.")

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
    filter_options = get_filter_options(data.normalized_trades)
    _initialize_trade_filters(data.normalized_trades)

    with st.sidebar:
        st.divider()
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

    render_section_title("Metricas Principais", "Core performance snapshot for the selected statement.")
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

    st.divider()

    render_section_title("Estado da Conta", data.account_metrics.health_summary)
    state_columns = st.columns(3)
    with state_columns[0]:
        render_metric_card("Traffic Light", data.account_metrics.traffic_light.title(), tone=_status_tone(data.account_metrics.traffic_light))
    with state_columns[1]:
        render_metric_card("Risk Zone", data.current_risk_zone.title(), tone=_status_tone(data.current_risk_zone))
    with state_columns[2]:
        render_metric_card("Current Drawdown %", f"{data.current_drawdown_pct:.2f}%", tone=_drawdown_tone(data.current_drawdown_pct))

    st.divider()

    render_section_title("Graficos", "Equity and drawdown curves for the current account selection.")
    chart_columns = st.columns(2)
    chart_columns[0].pyplot(create_equity_curve_chart(data.equity_timeline))
    chart_columns[1].pyplot(create_drawdown_curve_chart(data.drawdown_series))

    st.divider()
    render_trade_intelligence_panel(format_trade_intelligence(data.trade_intelligence))
    st.divider()
    render_strategy_analyzer_panel(format_strategy_analyzer(data.strategy_analyzer))

    st.divider()
    render_section_title("Trade Table", f"Filtered trades: {len(filtered_trade_rows)}")
    st.caption(f"Filtered trades: {len(filtered_trade_rows)}")
    trade_table = pd.DataFrame(filtered_trade_rows)
    st.dataframe(
        trade_table.style.format(
            {
                "pnl": "{:.4f}",
                "volume": "{:.2f}",
                "duration_minutes": "{:.2f}",
                "r_multiple": "{:.4f}",
            },
            na_rep="",
        ),
        use_container_width=True,
        hide_index=True,
    )


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


if __name__ == "__main__":
    main()
