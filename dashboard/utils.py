from __future__ import annotations

from pathlib import Path

import streamlit as st

from dashboard.components import get_dashboard_theme_css


def inject_dashboard_styles() -> None:
    st.markdown(get_dashboard_theme_css(), unsafe_allow_html=True)


def section_spacing() -> None:
    st.markdown("<div style='margin: 1.25rem 0;'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)


def render_premium_section_header(title: str, subtitle: str) -> None:
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


def save_uploaded_statement(project_root: Path, uploaded_file) -> Path:
    uploads_dir = project_root / "data" / "imports"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(uploaded_file.name).name
    saved_path = uploads_dir / safe_name
    saved_path.write_bytes(uploaded_file.getbuffer())

    return saved_path


def list_available_statements(project_root: Path) -> list[str]:
    imports_dir = project_root / "data" / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    return sorted([str(p) for p in imports_dir.glob("*.htm*")])


def safe_index(options: list[str], value: str) -> int:
    try:
        return options.index(value)
    except ValueError:
        return 0


def parse_cycle_target(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def resolve_selected_dates(selected_dates):
    if isinstance(selected_dates, tuple):
        if len(selected_dates) == 2:
            return selected_dates[0], selected_dates[1]
        if len(selected_dates) == 1:
            return selected_dates[0], selected_dates[0]
    return selected_dates, selected_dates


def status_tone(value: str) -> str:
    mapping = {"green": "good", "yellow": "warning", "red": "danger"}
    return mapping.get(value.lower(), "neutral")


def profit_tone(value: float) -> str:
    if value > 0:
        return "good"
    if value < 0:
        return "danger"
    return "neutral"


def drawdown_tone(value: float) -> str:
    if value <= 5:
        return "good"
    if value <= 10:
        return "warning"
    return "danger"