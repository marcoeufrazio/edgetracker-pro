from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.components import render_metric_card


def render_trade_intelligence_cards(trade_intelligence: Any) -> None:
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


def render_strategy_analyzer_cards(formatted_strategy: Any, raw_strategy: Any) -> None:
    def pick(*keys, default="-"):
        for source in (formatted_strategy, raw_strategy):
            if isinstance(source, dict):
                for key in keys:
                    value = source.get(key)
                    if value not in (None, "", []):
                        return value
            else:
                for key in keys:
                    value = getattr(source, key, None)
                    if value not in (None, "", []):
                        return value
        return default

    avg_duration = pick("average_trade_duration", "avg_trade_duration")
    best_duration = pick("best_duration_bucket")
    worst_duration = pick("worst_duration_bucket")
    best_size = pick("best_size_bucket")
    worst_size = pick("worst_size_bucket")
    best_win_cont = pick("best_continuation_after_win_streak", "best_win_streak_continuation")
    worst_win_cont = pick("worst_continuation_after_win_streak", "worst_win_streak_continuation")
    best_loss_recovery = pick("best_recovery_after_loss_streak")
    worst_loss_cont = pick("worst_continuation_after_loss_streak", "worst_loss_streak_continuation")

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
        render_metric_card(
            "Best Win-Streak Continuation",
            str(best_win_cont),
            tone="good" if best_win_cont != "-" else "neutral",
        )

    row3 = st.columns(3)
    with row3[0]:
        render_metric_card(
            "Worst Win-Streak Continuation",
            str(worst_win_cont),
            tone="danger" if worst_win_cont != "-" else "neutral",
        )
    with row3[1]:
        render_metric_card(
            "Best Loss Recovery",
            str(best_loss_recovery),
            tone="good" if best_loss_recovery != "-" else "neutral",
        )
    with row3[2]:
        render_metric_card(
            "Worst Loss Continuation",
            str(worst_loss_cont),
            tone="danger" if worst_loss_cont != "-" else "neutral",
        )