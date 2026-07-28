import streamlit as st

# =========================
# DEFINIÇÕES DE TEMA
# =========================
THEMES = {
    "dark": {
        "background": "#0e1117",
        "card": "#262730",
        "text": "#eaecef",
        "primary": "#4f9cff",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "error": "#e74c3c",
    },
    "light": {
        "background": "#f5f7fa",
        "card": "#ffffff",
        "text": "#111111",
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
    return THEMES[st.session_state.theme]


# =========================
# INJEÇÃO DE CSS
# =========================
def apply_theme():
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
        }}

        div[data-testid="stMetric"] {{
            background-color: {theme["card"]};
            padding: 15px;
            border-radius: 12px;
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

        </style>
        """,
        unsafe_allow_html=True,
    )
