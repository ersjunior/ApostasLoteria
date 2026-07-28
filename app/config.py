"""Configuração da aplicação Streamlit (secrets / env)."""

from __future__ import annotations

import os


def configure_runtime() -> None:
    """Aplica secrets do Streamlit Cloud como variáveis de ambiente."""
    try:
        import streamlit as st

        db_path = st.secrets.get("LOTTERIAS_DB_PATH")
        if db_path:
            os.environ.setdefault("LOTTERIAS_DB_PATH", str(db_path))
    except Exception:
        pass

    from loterias_core.repository import ensure_database

    ensure_database()
