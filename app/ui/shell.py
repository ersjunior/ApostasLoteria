"""Chrome global da UI Streamlit: tema (escuro fixo) + seletor de loteria no corpo."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.ui.lottery_selector import lottery_selector
from app.ui.theme_manager import apply_theme


def render_app_chrome() -> None:
    """
    Inicializa e aplica o tema **escuro** da aplicação.

    Deve ser chamado **após** ``st.set_page_config`` e antes do conteúdo.
    O tema claro foi descontinuado — a aplicação usa exclusivamente o tema
    escuro, alinhado ao boot definido em ``.streamlit/config.toml``.
    """
    st.session_state.theme = "dark"
    apply_theme()


def render_lottery_picker(
    label: str = "🎰 Loteria",
    *,
    key: str = "selected_lottery",
    help: str = "Modalidade usada nas análises desta página",
) -> tuple[str, dict[str, Any]]:
    """
    Seletor de loteria renderizado **no corpo** da página (abaixo do título).

    Usa a chave de sessão compartilhada ``selected_lottery`` para preservar a
    escolha ao navegar entre as páginas analíticas.
    """
    return lottery_selector(label, key=key, help=help, sidebar=False)
