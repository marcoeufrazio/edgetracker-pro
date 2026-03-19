from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from analytics.edge_score import calculate_edge_score
from dashboard.components import render_metric_card
from dashboard.data_loader import load_dashboard_data
from dashboard.utils import save_uploaded_statement


def render_multi_account_selector(
    project_root: Path,
    available_statements: list[str],
    current_statement: str,
) -> list[str]:
    comparison_options = [path for path in available_statements if path != current_statement]

    with st.container(border=True):
        st.markdown("#### Multi-Account Comparison")
        st.caption("Choose additional statements to compare against the current account.")

        uploaded_files = st.file_uploader(
            "Upload comparison statements",
            type=["html", "htm"],
            accept_multiple_files=True,
            help="Drag and drop one or more MT4 statements to compare with the current account.",
            key="comparison_uploads",
        )

        uploaded_paths: list[str] = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                saved_path = save_uploaded_statement(project_root, uploaded_file)
                uploaded_paths.append(str(saved_path))

            if uploaded_paths:
                st.success(f"{len(uploaded_paths)} comparison statement(s) uploaded successfully.")

        selected_existing = st.multiselect(
            "Existing comparison statements",
            options=comparison_options,
            default=[
                p
                for p in st.session_state.get("comparison_statement_paths", [])
                if p in comparison_options
            ],
            key="comparison_statement_paths",
        )

        combined_paths = []
        seen = set()

        for path in selected_existing + uploaded_paths:
            if path != current_statement and path not in seen:
                combined_paths.append(path)
                seen.add(path)

        return combined_paths


def load_comparison_accounts(
    current_statement_path: str,
    comparison_statement_paths: list[str],
    initial_balance: float,
    cycle_target: float | None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for path in comparison_statement_paths:
        if path == current_statement_path:
            continue

        try:
            comparison_data = load_dashboard_data(
                path,
                initial_balance=initial_balance,
                cycle_target=cycle_target,
            )
            comparison_edge = calculate_edge_score(
                profit_factor=comparison_data.performance.profit_factor,
                expectancy=comparison_data.performance.expectancy,
                win_rate=comparison_data.performance.win_rate,
                max_drawdown_pct=comparison_data.account_metrics.max_drawdown_pct,
                ulcer_index=comparison_data.account_metrics.ulcer_index,
            )
            results.append(
                {
                    "path": path,
                    "name": Path(path).name,
                    "data": comparison_data,
                    "edge_score": comparison_edge,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "path": path,
                    "name": Path(path).name,
                    "error": str(exc),
                }
            )

    return results


def render_multi_account_comparison(
    current_statement_path: str,
    current_data: Any,
    current_edge_score: Any,
    comparison_results: list[dict[str, Any]],
) -> pd.DataFrame:
    rows = [
        {
            "Account": Path(current_statement_path).name,
            "Net Profit": current_data.performance.net_profit,
            "Profit Factor": current_data.performance.profit_factor,
            "Win Rate %": current_data.performance.win_rate,
            "Max DD %": current_data.account_metrics.max_drawdown_pct,
            "Ulcer Index": current_data.account_metrics.ulcer_index,
            "Edge Score": current_edge_score.score,
            "Edge Class": current_edge_score.classification,
            "Best Symbol": getattr(current_data.trade_intelligence, "best_symbol", "-"),
            "Risk Zone": current_data.current_risk_zone.title(),
        }
    ]

    failed_accounts = []
    for item in comparison_results:
        if "error" in item:
            failed_accounts.append(f"{item['name']}: {item['error']}")
            continue

        comp_data = item["data"]
        comp_edge = item["edge_score"]
        rows.append(
            {
                "Account": item["name"],
                "Net Profit": comp_data.performance.net_profit,
                "Profit Factor": comp_data.performance.profit_factor,
                "Win Rate %": comp_data.performance.win_rate,
                "Max DD %": comp_data.account_metrics.max_drawdown_pct,
                "Ulcer Index": comp_data.account_metrics.ulcer_index,
                "Edge Score": comp_edge.score,
                "Edge Class": comp_edge.classification,
                "Best Symbol": getattr(comp_data.trade_intelligence, "best_symbol", "-"),
                "Risk Zone": comp_data.current_risk_zone.title(),
            }
        )

    comparison_df = pd.DataFrame(rows).sort_values(
        by=["Edge Score", "Net Profit"],
        ascending=[False, False],
    ).reset_index(drop=True)

    if len(comparison_df) == 1:
        st.info("Add one or more comparison statements in the sidebar to compare accounts.")
    else:
        top = comparison_df.iloc[0]
        bottom = comparison_df.iloc[-1]

        summary_cols = st.columns(3)
        with summary_cols[0]:
            render_metric_card("Best Account", str(top["Account"]), tone="good")
        with summary_cols[1]:
            render_metric_card("Top Edge Score", str(int(top["Edge Score"])), tone="good")
        with summary_cols[2]:
            render_metric_card("Lowest Edge Score", str(int(bottom["Edge Score"])), tone="danger")

        styled_df = comparison_df.style.format(
            {
                "Net Profit": "{:.2f}",
                "Profit Factor": "{:.4f}",
                "Win Rate %": "{:.2f}",
                "Max DD %": "{:.2f}",
                "Ulcer Index": "{:.2f}",
                "Edge Score": "{:.0f}",
            }
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    if failed_accounts:
        for msg in failed_accounts:
            st.warning(f"Comparison load failed: {msg}")

    return comparison_df