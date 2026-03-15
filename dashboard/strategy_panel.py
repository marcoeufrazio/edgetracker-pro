from __future__ import annotations

import streamlit as st


def render_trade_intelligence_panel(insights: dict[str, str]) -> None:
    st.subheader("Trade Intelligence")
    columns = st.columns(3)
    columns[0].metric("Best Day", insights["best_day"])
    columns[1].metric("Worst Day", insights["worst_day"])
    columns[2].metric("Best Hour", insights["best_hour"])

    columns = st.columns(3)
    columns[0].metric("Worst Hour", insights["worst_hour"])
    columns[1].metric("Best Symbol", insights["best_symbol"])
    columns[2].metric("Worst Symbol", insights["worst_symbol"])


def render_strategy_analyzer_panel(insights: dict[str, str]) -> None:
    st.subheader("Strategy Analyzer")
    columns = st.columns(2)
    columns[0].metric("Average Trade Duration", insights["average_trade_duration"])
    columns[1].metric("Best Duration Bucket", insights["best_duration_bucket"])

    columns = st.columns(2)
    columns[0].metric("Worst Duration Bucket", insights["worst_duration_bucket"])
    columns[1].metric("Best Size Bucket", insights["best_size_bucket"])

    columns = st.columns(2)
    columns[0].metric("Worst Size Bucket", insights["worst_size_bucket"])
    columns[1].metric("Best Continuation After Win Streak", insights["best_win_streak"])

    columns = st.columns(2)
    columns[0].metric("Worst Continuation After Win Streak", insights["worst_win_streak"])
    columns[1].metric("Best Recovery After Loss Streak", insights["best_loss_recovery"])

    st.metric("Worst Continuation After Loss Streak", insights["worst_loss_continuation"])
