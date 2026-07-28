"""Camada fina: cache Streamlit sobre o loader do core."""

import streamlit as st

from loterias_core.dataset import (
    enrich_dataset,
    handle_lotomania,
    handle_mais_milionaria,
    handle_supersete,
    normalize_columns,
    persist_dataset,
)
from loterias_core.dataset import (
    load_dataset as _load_dataset,
)
from loterias_core.dataset import (
    save_dataset as _save_dataset,
)

__all__ = [
    "enrich_dataset",
    "handle_lotomania",
    "handle_mais_milionaria",
    "handle_supersete",
    "load_dataset",
    "load_dataset_internal",
    "normalize_columns",
    "persist_dataset",
    "save_dataset",
]


@st.cache_data(ttl=3600)
def load_dataset(
    file_path: str,
    total_bolas: int,
    extra_fields: dict | None = None,
    multiple_draws: bool = False,
    special_handler: str | None = None,
):
    return _load_dataset(
        file_path=file_path,
        total_bolas=total_bolas,
        extra_fields=extra_fields,
        multiple_draws=multiple_draws,
        special_handler=special_handler,
    )


def load_dataset_internal(
    file_path: str,
    total_bolas: int,
    extra_fields: dict | None = None,
    multiple_draws: bool = False,
    special_handler: str | None = None,
):
    """Alias sem cache para compatibilidade."""
    return _load_dataset(
        file_path=file_path,
        total_bolas=total_bolas,
        extra_fields=extra_fields,
        multiple_draws=multiple_draws,
        special_handler=special_handler,
    )


def save_dataset(df, file_path: str, total_bolas: int):
    _save_dataset(df, file_path, total_bolas)
    st.cache_data.clear()
