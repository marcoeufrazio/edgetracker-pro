from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


def render_client_report_export(
    current_statement_path: str,
    data: Any,
    edge_score: Any,
    recommendations: list[dict[str, Any]],
    formatted_trade_intelligence: Any,
    formatted_strategy: Any,
    comparison_df: pd.DataFrame,
) -> None:
    report_markdown = build_client_report_markdown(
        current_statement_path=current_statement_path,
        data=data,
        edge_score=edge_score,
        recommendations=recommendations,
        formatted_trade_intelligence=formatted_trade_intelligence,
        formatted_strategy=formatted_strategy,
        comparison_df=comparison_df,
    )
    report_html = build_client_report_html(
        current_statement_path=current_statement_path,
        data=data,
        edge_score=edge_score,
        recommendations=recommendations,
        formatted_trade_intelligence=formatted_trade_intelligence,
        formatted_strategy=formatted_strategy,
        comparison_df=comparison_df,
    )

    download_cols = st.columns(2)
    with download_cols[0]:
        st.download_button(
            label="Download Markdown Report",
            data=report_markdown,
            file_name=f"{Path(current_statement_path).stem}_client_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with download_cols[1]:
        st.download_button(
            label="Download HTML Report",
            data=report_html,
            file_name=f"{Path(current_statement_path).stem}_client_report.html",
            mime="text/html",
            use_container_width=True,
        )

    st.caption("Tip: open the HTML report in a browser and print to PDF for client delivery.")


def build_client_report_markdown(
    current_statement_path: str,
    data: Any,
    edge_score: Any,
    recommendations: list[dict[str, Any]],
    formatted_trade_intelligence: Any,
    formatted_strategy: Any,
    comparison_df: pd.DataFrame,
) -> str:
    rec_lines = "\n".join([f"- {rec.get('message', '')}" for rec in recommendations]) or "- No recommendations available."
    ti = _to_flat_dict(formatted_trade_intelligence)
    sa = _to_flat_dict(formatted_strategy)

    comparison_section = ""
    if len(comparison_df) > 1:
        comparison_section = "\n## Multi-Account Comparison\n\n" + _dataframe_to_markdown_table(comparison_df) + "\n"

    return f"""# EdgeTracker-Pro Client Report

## Account
- Statement: {Path(current_statement_path).name}

## Executive Summary
- Net Profit: {data.performance.net_profit:.2f}
- Profit Factor: {data.performance.profit_factor:.4f}
- Win Rate: {data.performance.win_rate:.2f}%
- Expectancy: {data.performance.expectancy:.4f}
- Max Drawdown: {data.account_metrics.max_drawdown_pct:.2f}%
- Ulcer Index: {data.account_metrics.ulcer_index:.2f}
- Edge Score: {edge_score.score} / 100
- Edge Classification: {edge_score.classification}

## Account Status
- Traffic Light: {data.account_metrics.traffic_light.title()}
- Risk Zone: {data.current_risk_zone.title()}
- Current Drawdown: {data.current_drawdown_pct:.2f}%

## Recommendations
{rec_lines}

## Trade Intelligence
- Best Day: {ti.get("best_day", ti.get("best_day_of_week", "-"))}
- Worst Day: {ti.get("worst_day", ti.get("worst_day_of_week", "-"))}
- Best Hour: {ti.get("best_hour", ti.get("best_trading_hour", "-"))}
- Worst Hour: {ti.get("worst_hour", ti.get("worst_trading_hour", "-"))}
- Best Symbol: {ti.get("best_symbol", "-")}
- Worst Symbol: {ti.get("worst_symbol", "-")}

## Strategy Analyzer
- Average Trade Duration: {sa.get("average_trade_duration", sa.get("avg_trade_duration", "-"))}
- Best Duration Bucket: {sa.get("best_duration_bucket", "-")}
- Worst Duration Bucket: {sa.get("worst_duration_bucket", "-")}
- Best Size Bucket: {sa.get("best_size_bucket", "-")}
- Worst Size Bucket: {sa.get("worst_size_bucket", "-")}
- Best Win-Streak Continuation: {sa.get("best_continuation_after_win_streak", sa.get("best_win_streak_continuation", "-"))}
- Worst Win-Streak Continuation: {sa.get("worst_continuation_after_win_streak", sa.get("worst_win_streak_continuation", "-"))}
- Best Loss Recovery: {sa.get("best_recovery_after_loss_streak", "-")}
- Worst Loss Continuation: {sa.get("worst_continuation_after_loss_streak", sa.get("worst_loss_streak_continuation", "-"))}
{comparison_section}
"""


def build_client_report_html(
    current_statement_path: str,
    data: Any,
    edge_score: Any,
    recommendations: list[dict[str, Any]],
    formatted_trade_intelligence: Any,
    formatted_strategy: Any,
    comparison_df: pd.DataFrame,
) -> str:
    ti = _to_flat_dict(formatted_trade_intelligence)
    sa = _to_flat_dict(formatted_strategy)
    recommendation_items = "".join(
        f"<li>{escape(rec.get('message', ''))}</li>" for rec in recommendations
    ) or "<li>No recommendations available.</li>"

    comparison_html = ""
    if len(comparison_df) > 1:
        comparison_html = "<h2>Multi-Account Comparison</h2>" + comparison_df.to_html(index=False, border=0)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>EdgeTracker-Pro Client Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 32px;
    color: #111827;
}}
h1, h2 {{
    color: #0f172a;
}}
.card {{
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
    background: #f8fafc;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin-top: 12px;
}}
th, td {{
    border: 1px solid #d1d5db;
    padding: 8px 10px;
    text-align: left;
}}
th {{
    background: #e5e7eb;
}}
ul {{
    margin-top: 8px;
}}
</style>
</head>
<body>
<h1>EdgeTracker-Pro Client Report</h1>

<div class="card">
    <h2>Account</h2>
    <p><strong>Statement:</strong> {escape(Path(current_statement_path).name)}</p>
</div>

<div class="card">
    <h2>Executive Summary</h2>
    <p><strong>Net Profit:</strong> {data.performance.net_profit:.2f}</p>
    <p><strong>Profit Factor:</strong> {data.performance.profit_factor:.4f}</p>
    <p><strong>Win Rate:</strong> {data.performance.win_rate:.2f}%</p>
    <p><strong>Expectancy:</strong> {data.performance.expectancy:.4f}</p>
    <p><strong>Max Drawdown:</strong> {data.account_metrics.max_drawdown_pct:.2f}%</p>
    <p><strong>Ulcer Index:</strong> {data.account_metrics.ulcer_index:.2f}</p>
    <p><strong>Edge Score:</strong> {edge_score.score} / 100</p>
    <p><strong>Edge Classification:</strong> {escape(edge_score.classification)}</p>
</div>

<div class="card">
    <h2>Account Status</h2>
    <p><strong>Traffic Light:</strong> {escape(data.account_metrics.traffic_light.title())}</p>
    <p><strong>Risk Zone:</strong> {escape(data.current_risk_zone.title())}</p>
    <p><strong>Current Drawdown:</strong> {data.current_drawdown_pct:.2f}%</p>
</div>

<div class="card">
    <h2>Recommendations</h2>
    <ul>{recommendation_items}</ul>
</div>

<div class="card">
    <h2>Trade Intelligence</h2>
    <p><strong>Best Day:</strong> {escape(str(ti.get("best_day", ti.get("best_day_of_week", "-"))))}</p>
    <p><strong>Worst Day:</strong> {escape(str(ti.get("worst_day", ti.get("worst_day_of_week", "-"))))}</p>
    <p><strong>Best Hour:</strong> {escape(str(ti.get("best_hour", ti.get("best_trading_hour", "-"))))}</p>
    <p><strong>Worst Hour:</strong> {escape(str(ti.get("worst_hour", ti.get("worst_trading_hour", "-"))))}</p>
    <p><strong>Best Symbol:</strong> {escape(str(ti.get("best_symbol", "-")))}</p>
    <p><strong>Worst Symbol:</strong> {escape(str(ti.get("worst_symbol", "-")))}</p>
</div>

<div class="card">
    <h2>Strategy Analyzer</h2>
    <p><strong>Average Trade Duration:</strong> {escape(str(sa.get("average_trade_duration", sa.get("avg_trade_duration", "-"))))}</p>
    <p><strong>Best Duration Bucket:</strong> {escape(str(sa.get("best_duration_bucket", "-")))}</p>
    <p><strong>Worst Duration Bucket:</strong> {escape(str(sa.get("worst_duration_bucket", "-")))}</p>
    <p><strong>Best Size Bucket:</strong> {escape(str(sa.get("best_size_bucket", "-")))}</p>
    <p><strong>Worst Size Bucket:</strong> {escape(str(sa.get("worst_size_bucket", "-")))}</p>
</div>

{comparison_html}
</body>
</html>
"""


def _to_flat_dict(source: Any) -> dict[str, Any]:
    if isinstance(source, dict):
        return source
    if hasattr(source, "__dict__"):
        return dict(source.__dict__)
    return {}


def _dataframe_to_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "No comparison data available."

    columns = [str(col) for col in df.columns]
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    rows = []
    for _, row in df.iterrows():
        formatted_cells = []
        for value in row.tolist():
            if isinstance(value, float):
                formatted_cells.append(f"{value:.4f}".rstrip("0").rstrip("."))
            else:
                formatted_cells.append(str(value))
        rows.append("| " + " | ".join(formatted_cells) + " |")

    return "\n".join([header, separator] + rows)