"""Serviços core da API — delegam ao pacote loterias_core (SQLite)."""

from __future__ import annotations

import logging

import pandas as pd

from loterias_core.generator import generate_unique_combinations
from loterias_core.lotteries import LOTTERIES_BY_KEY
from loterias_core.repository import (
    get_cache_status,
    get_health_payload,
    load_lottery_dataframe,
    update_lottery_from_raw,
)
from loterias_core.scraper import DataSource, ScraperError, download_lottery_data
from loterias_core.validator import check_game

logger = logging.getLogger(__name__)

MEGASENA_KEY = "megasena"
MEGASENA_CONFIG = LOTTERIES_BY_KEY[MEGASENA_KEY].to_dict()


def get_dataset_status() -> dict:
    """Metadados da Mega-Sena para /health e GET /dataset/ (compatibilidade)."""
    status = get_cache_status(MEGASENA_KEY)
    from loterias_core.storage import get_db_path

    return {
        "exists": status["exists"],
        "path": get_db_path(),
        "last_update": status["last_update"],
        "last_concurso": status["last_concurso"],
        "total_records": status["total_records"] if status["exists"] else None,
    }


def get_all_lotteries_status() -> dict:
    """Status de cache por modalidade."""
    return get_cache_status()


def load_dataset() -> pd.DataFrame:
    """Carrega o dataset da Mega-Sena do SQLite."""
    return load_lottery_dataframe(MEGASENA_KEY)


def update_dataset(source: DataSource | str = DataSource.AUTO, *, incremental: bool = True):
    """Atualiza a Mega-Sena baixando da Caixa e persistindo incrementalmente."""
    logger.info("Iniciando download da base Mega-Sena (source=%s, incremental=%s)", source, incremental)
    try:
        df_raw = download_lottery_data(MEGASENA_KEY, source=source)
    except ScraperError as exc:
        logger.exception("Scraper falhou ao baixar Mega-Sena")
        raise RuntimeError(str(exc)) from exc

    processed, inserted = update_lottery_from_raw(
        MEGASENA_KEY,
        df_raw,
        MEGASENA_CONFIG,
        incremental=incremental,
    )
    logger.info(
        "Dataset Mega-Sena atualizado — %d novos registros, total %d",
        inserted,
        len(processed),
    )
    return processed


def verify_game(numbers: list[int]) -> bool:
    """Verifica se um jogo já foi sorteado."""
    df = load_dataset()
    return check_game(sorted(numbers), df)


def generate_unique_combination_games(n: int = 10):
    """Gera combinações inéditas com base no histórico da Mega-Sena."""
    df = load_dataset()
    return generate_unique_combinations(df, n_games=n, total_bolas=6, universo=60)


def health_info() -> dict:
    """Informações completas para GET /health."""
    return get_health_payload()
