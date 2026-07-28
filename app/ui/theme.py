import streamlit as st

from app.ui.theme_manager import get_theme

# =========================
# CORES DO PROJETO
# =========================
PRIMARY_COLOR = "#1f77b4"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
ERROR_COLOR = "#e74c3c"
BACKGROUND_COLOR = "#0e1117"
CARD_COLOR = "#262730"


# =========================
# COMPONENTES DE UI
# =========================
def page_title(title: str, subtitle: str | None = None):
    theme = get_theme()

    st.markdown(
        f"""
        <h1 style="color:{theme["primary"]}; margin-bottom: 0;">
            {title}
        </h1>
        """,
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f"""
            <p style="color:#888; margin-top: 0;">
                {subtitle}
            </p>
            """,
            unsafe_allow_html=True,
        )


def section(title: str):
    theme = get_theme()

    st.markdown(
        f"""
        <h3 style="
            border-bottom: 2px solid {theme["primary"]};
            padding-bottom: 5px;
            margin-top: 30px;
        ">
            {title}
        </h3>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, icon: str):
    theme = get_theme()

    st.markdown(
        f"""
        <div style="
            background-color:{theme["card"]};
            padding:20px;
            border-radius:12px;
            text-align:center;
        ">
            <div style="font-size:28px">{icon}</div>
            <div style="font-size:14px; color:#888">{label}</div>
            <div style="font-size:24px; font-weight:bold">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def game_card(
    title: str,
    numbers: list[int],
    status: str,
    accent_color="#2563eb",
    background_color="rgba(255,255,255,0.05)",
):
    st.markdown(
        f"""
        <div style="
            padding:15px;
            border-radius:10px;
            background:{background_color};
            border-left:6px solid {accent_color};
            margin-bottom:15px;
        ">
            <strong>{title}</strong><br><br>
            <div style="font-size:18px; letter-spacing:2px;">
                {" • ".join(f"{n:02d}" for n in numbers)}
            </div>
            <div style="margin-top:8px; color:#9ca3af;">
                {status}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# def game_card(title: str, numbers: list[int], status: str):
#    nums = " • ".join(f"{n:02d}" for n in numbers)
#
#    st.markdown(
#        f"""
#        <div style="
#            background-color:{CARD_COLOR};
#            padding:15px;
#            border-radius:14px;
#            margin-bottom:15px;
#            text-align:center;
#        ">
#            <div style="font-size:18px; font-weight:bold;">{title}</div>
#            <div style="font-size:18px; margin:10px 0;">{nums}</div>
#            <div style="color:#ff6b6b;">{status}</div>
#        </div>
#        """,
#        unsafe_allow_html=True,
#    )


def card(title: str, content: str):
    st.markdown(
        f"""
        <div style="
            background-color:{CARD_COLOR};
            padding:20px;
            border-radius:10px;
            margin-bottom:15px;
        ">
            <h4>{title}</h4>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_message(message: str, status: str = "info"):
    colors = {
        "success": SUCCESS_COLOR,
        "warning": WARNING_COLOR,
        "error": ERROR_COLOR,
        "info": PRIMARY_COLOR,
    }

    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {colors.get(status, PRIMARY_COLOR)};
            padding: 10px 15px;
            margin: 10px 0;
            background-color: {CARD_COLOR};
        ">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


RESPONSIBLE_GAMING_URL = "https://jogadoresanonimos.com.br/"


def responsible_gaming_footer() -> None:
    """Rodapé com aviso educacional e link de apoio a jogo compulsivo."""
    st.markdown("---")
    st.caption(
        "Este projeto é **estritamente educacional** e analítico — nenhuma estatística "
        "garante prêmios. Loterias são jogos de azar. "
        f"Se você ou alguém próximo tem dificuldade com jogo compulsivo, "
        f"busque apoio em [Jogadores Anônimos]({RESPONSIBLE_GAMING_URL})."
    )
