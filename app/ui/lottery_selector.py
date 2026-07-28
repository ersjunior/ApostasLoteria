"""Seletor de loteria reutilizável (Streamlit)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.core.lotteries import LOTTERIES


def lottery_selector(
    label: str = "Escolha a loteria",
    *,
    key: str = "selected_lottery",
    help: str | None = "Escolha a loteria para análise",
    sidebar: bool = False,
) -> tuple[str, dict[str, Any]]:
    """
    Renderiza um selectbox com as modalidades do catálogo.

    Usa ``key`` de sessão (padrão compartilhado entre páginas analíticas)
    para persistir a escolha ao navegar.
    """
    widget = st.sidebar.selectbox if sidebar else st.selectbox
    name = widget(label, list(LOTTERIES.keys()), key=key, help=help)
    return name, LOTTERIES[name]
