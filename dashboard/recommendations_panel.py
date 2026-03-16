from typing import Dict, List
import streamlit as st


def render_recommendations_panel(recommendations: List[Dict]) -> None:
    if not recommendations:
        st.info("No recommendations available yet.")
        return

    type_config = {
        "risk": {"icon": "⚠️", "tone": "warning"},
        "risk_management": {"icon": "🛡️", "tone": "danger"},
        "performance": {"icon": "📈", "tone": "success"},
        "timing": {"icon": "🕒", "tone": "info"},
        "general": {"icon": "💡", "tone": "info"},
    }

    for rec in recommendations:
        rec_type = rec.get("type", "general")
        message = rec.get("message", "")
        config = type_config.get(rec_type, type_config["general"])
        content = f"{config['icon']} {message}"

        if config["tone"] == "warning":
            st.warning(content)
        elif config["tone"] == "danger":
            st.error(content)
        elif config["tone"] == "success":
            st.success(content)
        else:
            st.info(content)