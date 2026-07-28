import streamlit as st

# =========================
# DEFINIÇÕES DE TEMA
# =========================
THEMES = {
    "dark": {
        "background": "#0e1117",
        "secondary": "#1c1f26",
        "card": "#262730",
        "text": "#eaecef",
        "muted": "#9ca3af",
        "primary": "#4f9cff",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "error": "#e74c3c",
    },
    "light": {
        "background": "#f5f7fa",
        "secondary": "#e8ecf1",
        "card": "#ffffff",
        "text": "#111111",
        "muted": "#6b7280",
        "primary": "#3366ff",
        "success": "#27ae60",
        "warning": "#e67e22",
        "error": "#c0392b",
    },
}


# =========================
# ESTADO DO TEMA
# =========================
def init_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


def get_theme():
    name = st.session_state.get("theme", "dark")
    return THEMES.get(name, THEMES["dark"])


# =========================
# INJEÇÃO DE CSS
# =========================
def apply_theme():
    """Aplica CSS runtime. O ``config.toml`` define o boot; este CSS sobrescreve a sessão."""
    theme = get_theme()

    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            background-color: {theme["background"]};
            color: {theme["text"]};
        }}

        .stApp {{
            background-color: {theme["background"]};
            color: {theme["text"]};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {theme["secondary"]};
        }}

        section[data-testid="stSidebar"] * {{
            color: {theme["text"]};
        }}

        div[data-testid="stMetric"] {{
            background-color: {theme["card"]};
            padding: 15px;
            border-radius: 12px;
            border: 1px solid {theme["secondary"]};
        }}

        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {theme["muted"]} !important;
        }}

        .stButton>button {{
            background-color: {theme["primary"]};
            color: white;
            border-radius: 10px;
            padding: 10px 16px;
            border: none;
        }}

        .stButton>button:hover {{
            opacity: 0.9;
        }}

        div[data-baseweb="select"] > div,
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {{
            background-color: {theme["card"]} !important;
            color: {theme["text"]} !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )
