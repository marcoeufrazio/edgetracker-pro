from __future__ import annotations


def get_dashboard_theme_css() -> str:
    return """
    <style>
    :root {
        --etp-bg: var(--background-color);
        --etp-surface: color-mix(in srgb, var(--secondary-background-color) 72%, var(--background-color) 28%);
        --etp-surface-strong: color-mix(in srgb, var(--secondary-background-color) 88%, var(--background-color) 12%);
        --etp-border: color-mix(in srgb, var(--text-color) 12%, transparent);
        --etp-border-strong: color-mix(in srgb, var(--text-color) 18%, transparent);
        --etp-text: var(--text-color);
        --etp-text-muted: color-mix(in srgb, var(--text-color) 68%, transparent);
        --etp-good: #1f9d68;
        --etp-warning: #d9822b;
        --etp-danger: #d64545;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, color-mix(in srgb, var(--primary-color) 8%, transparent) 0%, transparent 28%),
            linear-gradient(180deg, color-mix(in srgb, var(--background-color) 94%, var(--secondary-background-color) 6%) 0%, var(--background-color) 100%);
        color: var(--etp-text);
    }

    .etp-section-title {
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--etp-text);
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
    }

    .etp-section-caption {
        color: var(--etp-text-muted);
        margin-bottom: 0.85rem;
    }

    .etp-card {
        border-radius: 18px;
        padding: 1rem 1rem 0.95rem 1rem;
        border: 1px solid var(--etp-border);
        background: linear-gradient(180deg, color-mix(in srgb, var(--etp-surface) 86%, transparent) 0%, color-mix(in srgb, var(--etp-bg) 94%, transparent) 100%);
        box-shadow: 0 10px 24px color-mix(in srgb, var(--text-color) 8%, transparent);
        min-height: 108px;
        backdrop-filter: blur(6px);
    }

    .etp-card-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--etp-text-muted);
        margin-bottom: 0.6rem;
    }

    .etp-card-value {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--etp-text);
        line-height: 1.1;
    }

    .etp-card-good {
        border-color: color-mix(in srgb, var(--etp-good) 28%, var(--etp-border));
        background: linear-gradient(180deg, color-mix(in srgb, var(--etp-good) 14%, var(--etp-surface-strong)) 0%, color-mix(in srgb, var(--etp-good) 4%, var(--etp-bg)) 100%);
    }

    .etp-card-warning {
        border-color: color-mix(in srgb, var(--etp-warning) 30%, var(--etp-border));
        background: linear-gradient(180deg, color-mix(in srgb, var(--etp-warning) 14%, var(--etp-surface-strong)) 0%, color-mix(in srgb, var(--etp-warning) 4%, var(--etp-bg)) 100%);
    }

    .etp-card-danger {
        border-color: color-mix(in srgb, var(--etp-danger) 30%, var(--etp-border));
        background: linear-gradient(180deg, color-mix(in srgb, var(--etp-danger) 14%, var(--etp-surface-strong)) 0%, color-mix(in srgb, var(--etp-danger) 4%, var(--etp-bg)) 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, color-mix(in srgb, var(--secondary-background-color) 92%, var(--background-color) 8%) 0%, color-mix(in srgb, var(--secondary-background-color) 72%, var(--background-color) 28%) 100%);
        border-right: 1px solid var(--etp-border);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaptionContainer {
        color: var(--etp-text);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--etp-border-strong);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 24px color-mix(in srgb, var(--text-color) 7%, transparent);
        background: color-mix(in srgb, var(--etp-surface) 90%, transparent);
    }

    [data-testid="stDataFrame"] [data-testid="stTable"] {
        color: var(--etp-text);
    }

    div[data-testid="stVerticalBlock"] > div:has(> .element-container .etp-card) {
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
    }

    [data-testid="stDivider"] {
        opacity: 0.75;
    }
    </style>
    """
