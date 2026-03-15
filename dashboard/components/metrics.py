from __future__ import annotations

import streamlit as st


def render_section_title(title: str, caption: str | None = None) -> None:
    st.markdown(f"<div class='etp-section-title'>{title}</div>", unsafe_allow_html=True)
    if caption:
        st.markdown(f"<div class='etp-section-caption'>{caption}</div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, tone: str = "neutral") -> None:
    st.markdown(
        (
            f"<div class='etp-card etp-card-{tone}'>"
            f"<div class='etp-card-label'>{label}</div>"
            f"<div class='etp-card-value'>{value}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
