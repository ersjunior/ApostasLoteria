"""Chrome global da UI Streamlit: tema + sidebar (loteria / claro-escuro)."""

from __future__ import annotations

from typing import Any, Literal, overload

import streamlit as st

from app.ui.lottery_selector import lottery_selector
from app.ui.theme_manager import apply_theme, init_theme


def _sync_theme_from_radio() -> None:
    """Radio Escuro/Claro ↔ ``st.session_state.theme``."""
    labels = ("Escuro", "Claro")
    values = {"Escuro": "dark", "Claro": "light"}
    current = st.session_state.get("theme", "dark")
    default_label = "Escuro" if current == "dark" else "Claro"
    index = labels.index(default_label)

    choice = st.sidebar.radio(
        "Tema",
        labels,
        index=index,
        key="theme_radio",
        horizontal=True,
        help="O tema nativo do Streamlit permanece o do config.toml; "
        "este controle ajusta cores via CSS em runtime.",
    )
    st.session_state.theme = values[choice]


@overload
def render_app_chrome(*, show_lottery: Literal[True] = True) -> tuple[str, dict[str, Any]]: ...


@overload
def render_app_chrome(*, show_lottery: Literal[False]) -> None: ...


def render_app_chrome(*, show_lottery: bool = True) -> tuple[str, dict[str, Any]] | None:
    """
    Inicializa tema e renderiza a sidebar global.

    Deve ser chamado **após** ``st.set_page_config``.

    Returns:
        ``(nome, config)`` da loteria quando ``show_lottery`` é True; senão ``None``.
    """
    init_theme()

    st.sidebar.markdown("## Controles")
    st.sidebar.caption("Preferências compartilhadas entre as páginas.")

    selected: tuple[str, dict[str, Any]] | None = None
    if show_lottery:
        selected = lottery_selector(
            "Loteria",
            key="selected_lottery",
            help="Modalidade usada nas páginas analíticas",
            sidebar=True,
        )

    _sync_theme_from_radio()
    apply_theme()
    st.sidebar.markdown("---")
    return selected
