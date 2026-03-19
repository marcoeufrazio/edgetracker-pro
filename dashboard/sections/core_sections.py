from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.components import render_metric_card


def render_health_banner(data: Any, recommendations: list[dict[str, Any]]) -> None:
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


def render_edge_score_banner(edge_score) -> None:
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


def render_core_metrics(data: Any, profit_tone) -> None:
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
            tone=profit_tone(data.performance.net_profit),
        )


def render_account_status(data: Any, status_tone, profit_tone, drawdown_tone) -> None:
    summary_columns = st.columns(3)
    with summary_columns[0]:
        render_metric_card(
            "Profit",
            f"{data.performance.net_profit:.2f}",
            tone=profit_tone(data.performance.net_profit),
        )
    with summary_columns[1]:
        render_metric_card(
            "Max Drawdown",
            f"{data.account_metrics.max_drawdown_pct:.2f}%",
            tone=drawdown_tone(data.account_metrics.max_drawdown_pct),
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
            tone=status_tone(traffic_value),
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
            tone=status_tone(risk_value),
        )

    with state_columns[2]:
        render_metric_card(
            "Current Drawdown %",
            f"{data.current_drawdown_pct:.2f}%",
            tone=drawdown_tone(data.current_drawdown_pct),
        )