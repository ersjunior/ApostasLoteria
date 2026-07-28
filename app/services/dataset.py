"""Camada fina: cache Streamlit sobre o repositório SQLite."""

import streamlit as st

from loterias_core.dataset import (
    enrich_dataset,
    handle_lotomania,
    handle_mais_milionaria,
    handle_supersete,
    load_dataset_by_key,
    normalize_columns,
    persist_dataset,
)
from loterias_core.dataset import (
    load_dataset as _load_dataset_from_xlsx,
)
from loterias_core.dataset import (
    save_dataset as _save_dataset,
)
from loterias_core.repository import get_cache_status, update_lottery_from_raw

__all__ = [
    "enrich_dataset",
    "get_lottery_cache_status",
    "handle_lotomania",
    "handle_mais_milionaria",
    "handle_supersete",
    "load_dataset",
    "load_dataset_internal",
    "normalize_columns",
    "persist_dataset",
    "save_dataset",
    "update_lottery_cache",
]


@st.cache_data(ttl=3600)
def load_dataset(
    lottery_key: str,
    total_bolas: int | None = None,
    extra_fields: dict | None = None,
    multiple_draws: bool = False,
    special_handler: str | None = None,
):
    """Carrega dataset do SQLite (parâmetros extras mantidos por compatibilidade de assinatura)."""
    del total_bolas, extra_fields, multiple_draws, special_handler
    return load_dataset_by_key(lottery_key)


def load_dataset_internal(lottery_key: str, **_kwargs):
    """Alias sem cache para compatibilidade."""
    return load_dataset_by_key(lottery_key)


def get_lottery_cache_status(lottery_key: str | None = None):
    return get_cache_status(lottery_key)


def update_lottery_cache(lottery_key: str, config: dict, *, incremental: bool = True):
    """Baixa da Caixa e atualiza cache incremental da modalidade."""
    from loterias_core.scraper import download_lottery_data

    df_raw = download_lottery_data(lottery_key)
    processed, inserted = update_lottery_from_raw(
        lottery_key,
        df_raw,
        config,
        incremental=incremental,
    )
    st.cache_data.clear()
    return processed, inserted


def save_dataset(df, file_path: str, total_bolas: int):
    _save_dataset(df, file_path, total_bolas)
    st.cache_data.clear()
