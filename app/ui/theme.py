from __future__ import annotations

from typing import Any

import streamlit as st

from app.ui.theme_manager import get_theme

# =========================
# CORES DO PROJETO (fallback / status)
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
            <p style="color:{theme["muted"]}; margin-top: 0;">
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


def lottery_badge(name: str, config: dict[str, Any], detail: str | None = None) -> None:
    """Badge compacto da modalidade selecionada na sidebar."""
    theme = get_theme()
    accent = config.get("color") or theme["primary"]
    icon = config.get("icon", "🎲")
    body = detail or f"{config.get('total_bolas', '?')} dezenas · universo {config.get('universo', '?')}"
    st.markdown(
        f"""
        <div style="
            margin: 8px 0 16px 0;
            padding: 10px 15px;
            border-left: 5px solid {accent};
            background-color: {theme["card"]};
            border-radius: 6px;
            border: 1px solid {theme["secondary"]};
            border-left-width: 5px;
        ">
            <strong>{icon} {name}</strong><br>
            <span style="color:{theme["muted"]}; font-size:14px;">{body}</span>
        </div>
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
            border: 1px solid {theme["secondary"]};
        ">
            <div style="font-size:28px">{icon}</div>
            <div style="font-size:14px; color:{theme["muted"]};">{label}</div>
            <div style="font-size:24px; font-weight:bold; color:{theme["text"]};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def game_card(
    title: str,
    numbers: list[int],
    status: str,
    accent_color="#2563eb",
    background_color=None,
    extras: dict | None = None,
):
    theme = get_theme()
    bg = background_color if background_color is not None else theme["card"]
    muted = theme["muted"]

    extras_html = ""
    if extras:
        lines = []
        for field, values in extras.items():
            label = field.capitalize()
            nums = " • ".join(f"{int(n):02d}" for n in values)
            lines.append(f"{label}: {nums}")
        extras_html = (
            f"<div style='margin-top:10px; font-size:15px; letter-spacing:1px; color:{muted};'>"
            + "<br>".join(lines)
            + "</div>"
        )

    st.markdown(
        f"""
        <div style="
            padding:15px;
            border-radius:10px;
            background:{bg};
            border-left:6px solid {accent_color};
            margin-bottom:15px;
            color:{theme["text"]};
        ">
            <strong>{title}</strong><br><br>
            <div style="font-size:18px; letter-spacing:2px;">
                {" • ".join(f"{n:02d}" for n in numbers)}
            </div>
            {extras_html}
            <div style="margin-top:8px; color:{muted};">
                {status}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, content: str):
    theme = get_theme()

    st.markdown(
        f"""
        <div style="
            background-color:{theme["card"]};
            padding:20px;
            border-radius:10px;
            margin-bottom:15px;
            border: 1px solid {theme["secondary"]};
            color:{theme["text"]};
        ">
            <h4 style="color:{theme["text"]}; margin-top:0;">{title}</h4>
            <p style="color:{theme["muted"]};">{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_message(message: str, status: str = "info"):
    theme = get_theme()
    colors = {
        "success": theme["success"],
        "warning": theme["warning"],
        "error": theme["error"],
        "info": theme["primary"],
    }

    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {colors.get(status, theme["primary"])};
            padding: 10px 15px;
            margin: 10px 0;
            background-color: {theme["card"]};
            color: {theme["text"]};
            border-radius: 6px;
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
