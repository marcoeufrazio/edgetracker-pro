from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from dashboard.components import render_metric_card


def render_equity_intelligence(trades: list[Any]) -> None:
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


def render_risk_behaviour_analyzer(trades: list[Any]) -> None:
    if not trades:
        st.info("No trades available for behaviour analysis.")
        return

    ordered_trades = sorted(
        [trade for trade in trades if getattr(trade, "closed_at", None) is not None],
        key=lambda x: x.closed_at,
    )
    if not ordered_trades:
        st.info("No trades available for behaviour analysis.")
        return

    volumes = []
    overtrading_days = 0
    revenge_events = 0
    size_escalation_events = 0
    post_loss_pressure = 0

    day_counts: dict[Any, int] = {}
    prev_trade = None

    for trade in ordered_trades:
        closed_at = getattr(trade, "closed_at", None)
        pnl = float(getattr(trade, "net_profit", 0.0) or 0.0)
        volume = float(getattr(trade, "volume", 0.0) or 0.0)
        volumes.append(volume)

        if closed_at is not None:
            day_counts[closed_at.date()] = day_counts.get(closed_at.date(), 0) + 1

        if prev_trade is not None:
            prev_pnl = float(getattr(prev_trade, "net_profit", 0.0) or 0.0)
            prev_volume = float(getattr(prev_trade, "volume", 0.0) or 0.0)
            prev_closed = getattr(prev_trade, "closed_at", None)

            if prev_pnl < 0 and prev_closed and closed_at:
                minutes_gap = (closed_at - prev_closed).total_seconds() / 60
                if minutes_gap <= 10:
                    revenge_events += 1
                if volume > prev_volume:
                    size_escalation_events += 1
                if pnl < 0:
                    post_loss_pressure += 1

        prev_trade = trade

    overtrading_threshold = max(15, int(pd.Series(list(day_counts.values())).mean() * 1.8)) if day_counts else 15
    overtrading_days = sum(1 for count in day_counts.values() if count >= overtrading_threshold)

    avg_volume = sum(volumes) / len(volumes) if volumes else 0.0
    max_volume = max(volumes) if volumes else 0.0

    escalation_ratio = (size_escalation_events / max(1, len(ordered_trades) - 1)) * 100
    revenge_ratio = (revenge_events / max(1, len(ordered_trades) - 1)) * 100

    row1 = st.columns(4)
    with row1[0]:
        render_metric_card("Overtrading Days", str(overtrading_days), tone="warning" if overtrading_days else "neutral")
    with row1[1]:
        render_metric_card("Revenge Signals", str(revenge_events), tone="danger" if revenge_events else "neutral")
    with row1[2]:
        render_metric_card("Size Escalations", str(size_escalation_events), tone="warning" if size_escalation_events else "neutral")
    with row1[3]:
        render_metric_card("Post-Loss Pressure", str(post_loss_pressure), tone="danger" if post_loss_pressure else "neutral")

    row2 = st.columns(4)
    with row2[0]:
        render_metric_card("Avg Volume", f"{avg_volume:.2f}", tone="neutral")
    with row2[1]:
        render_metric_card("Max Volume", f"{max_volume:.2f}", tone="neutral")
    with row2[2]:
        render_metric_card("Escalation Ratio", f"{escalation_ratio:.1f}%", tone="warning" if escalation_ratio >= 20 else "neutral")
    with row2[3]:
        render_metric_card("Revenge Ratio", f"{revenge_ratio:.1f}%", tone="danger" if revenge_ratio >= 15 else "neutral")

    behaviour_messages = []
    if overtrading_days > 0:
        behaviour_messages.append(f"⚠️ Overtrading detected on {overtrading_days} trading day(s).")
    if revenge_events > 0:
        behaviour_messages.append(f"⚠️ {revenge_events} possible revenge-trading signal(s) after losses.")
    if size_escalation_events > 0:
        behaviour_messages.append(f"🛡️ Position size increased after losses {size_escalation_events} time(s).")
    if post_loss_pressure > 0:
        behaviour_messages.append(f"🔻 Consecutive underperformance after losses detected {post_loss_pressure} time(s).")

    if behaviour_messages:
        for message in behaviour_messages:
            st.warning(message)
    else:
        st.success("No strong negative risk behaviour patterns detected.")


def render_ai_strategy_coach(
    data: Any,
    edge_score: Any,
    formatted_trade_intelligence: Any,
    formatted_strategy: Any,
) -> None:
    coach_notes: list[str] = []

    def pick(source: Any, *keys, default="-"):
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

    best_symbol = pick(formatted_trade_intelligence, "best_symbol")
    worst_symbol = pick(formatted_trade_intelligence, "worst_symbol")
    best_day = pick(formatted_trade_intelligence, "best_day", "best_day_of_week")
    worst_day = pick(formatted_trade_intelligence, "worst_day", "worst_day_of_week")
    best_hour = pick(formatted_trade_intelligence, "best_hour", "best_trading_hour")
    worst_hour = pick(formatted_trade_intelligence, "worst_hour", "worst_trading_hour")
    best_duration = pick(formatted_strategy, "best_duration_bucket")
    worst_duration = pick(formatted_strategy, "worst_duration_bucket")

    if best_symbol != "-":
        coach_notes.append(f"📈 Lean into {best_symbol}, which is currently your strongest symbol.")
    if worst_symbol != "-":
        coach_notes.append(f"🛑 Reduce exposure to {worst_symbol} until performance stabilises.")
    if best_day != "-":
        coach_notes.append(f"🗓️ Your edge appears strongest on {best_day}.")
    if worst_day != "-":
        coach_notes.append(f"⚠️ Review decision quality on {worst_day}, your weakest day so far.")
    if best_hour != "-":
        coach_notes.append(f"🕒 Performance looks stronger around {best_hour}:00.")
    if worst_hour != "-":
        coach_notes.append(f"⏱️ Avoid forcing setups around {worst_hour}:00.")
    if best_duration != "-":
        coach_notes.append(f"🎯 {best_duration} duration trades currently show the cleanest edge.")
    if worst_duration != "-":
        coach_notes.append(f"📉 {worst_duration} duration trades appear weaker and may need tighter management.")

    if data.performance.profit_factor < 1.0:
        coach_notes.append("🛡️ Profit factor is below 1.0, so improving reward-to-risk should be a top priority.")
    if data.performance.expectancy < 0:
        coach_notes.append("📊 Expectancy is negative, which suggests the current execution pattern needs refinement.")
    if data.account_metrics.max_drawdown_pct > 10:
        coach_notes.append("🔻 Drawdown is elevated. Trade smaller until recovery quality improves.")
    if edge_score.score >= 70:
        coach_notes.append("🚀 Edge score is strong. Focus on consistency rather than adding complexity.")
    elif edge_score.score < 55:
        coach_notes.append("🧠 Edge score is fragile. Focus on preserving capital and removing weak setups.")

    if not coach_notes:
        coach_notes.append("💡 No critical coaching signals detected. Maintain discipline and keep collecting data.")

    for note in coach_notes[:6]:
        st.info(note)


def render_session_analyzer(trades: list[Any]) -> None:
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


def render_distribution_charts(trades: list[Any]) -> None:
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