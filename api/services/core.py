"""Serviços core da API — delegam ao pacote loterias_core (SQLite)."""

from __future__ import annotations

import logging

import pandas as pd

from loterias_core.generator import generate_unique_combinations
from loterias_core.lotteries import LOTTERIES_BY_KEY, LotteryConfig
from loterias_core.repository import (
    get_cache_status,
    get_health_payload,
    load_lottery_dataframe,
    update_lottery_from_raw,
)
from loterias_core.scraper import DataSource, ScraperError, download_lottery_data
from loterias_core.validator import check_game

logger = logging.getLogger(__name__)

DEFAULT_LOTTERY_KEY = "megasena"


def _config(lottery_key: str) -> LotteryConfig:
    config = LOTTERIES_BY_KEY.get(lottery_key)
    if config is None:
        raise KeyError(f"Loteria desconhecida: {lottery_key}")
    return config


def get_dataset_status(lottery_key: str = DEFAULT_LOTTERY_KEY) -> dict:
    """Metadados de uma modalidade para GET /dataset/ e compatibilidade."""
    status = get_cache_status(lottery_key)
    from loterias_core.storage import get_db_path

    return {
        "exists": status["exists"],
        "path": get_db_path(),
        "lottery_key": lottery_key,
        "last_update": status["last_update"],
        "last_concurso": status["last_concurso"],
        "total_records": status["total_records"] if status["exists"] else None,
    }


def get_all_lotteries_status() -> dict:
    """Status de cache por modalidade."""
    return get_cache_status()


def list_lotteries() -> list[dict]:
    """Catálogo + status de cache para GET /lotteries."""
    cache = get_cache_status()
    items: list[dict] = []
    for key, cfg in LOTTERIES_BY_KEY.items():
        status = cache.get(key, {})
        items.append(
            {
                "key": key,
                "name": cfg.name,
                "total_bolas": cfg.total_bolas,
                "universo": cfg.universo,
                "exists": bool(status.get("exists")),
                "total_records": status.get("total_records", 0),
                "last_update": status.get("last_update"),
                "last_concurso": status.get("last_concurso"),
            }
        )
    return items


def load_dataset(lottery_key: str = DEFAULT_LOTTERY_KEY) -> pd.DataFrame:
    """Carrega o dataset de uma modalidade do SQLite."""
    return load_lottery_dataframe(lottery_key)


def update_dataset(
    lottery_key: str = DEFAULT_LOTTERY_KEY,
    source: DataSource | str = DataSource.AUTO,
    *,
    incremental: bool = True,
):
    """Baixa da Caixa e persiste incrementalmente a modalidade informada."""
    config = _config(lottery_key)
    logger.info(
        "Iniciando download da base %s (source=%s, incremental=%s)",
        config.name,
        source,
        incremental,
    )
    try:
        df_raw = download_lottery_data(lottery_key, source=source)
    except ScraperError as exc:
        logger.exception("Scraper falhou ao baixar %s", config.name)
        raise RuntimeError(str(exc)) from exc

    processed, inserted = update_lottery_from_raw(
        lottery_key,
        df_raw,
        config.to_dict(),
        incremental=incremental,
    )
    logger.info(
        "Dataset %s atualizado — %d novos registros, total %d",
        config.name,
        inserted,
        len(processed),
    )
    return processed


def verify_game(
    lottery_key: str,
    numbers: list[int],
    extras: dict[str, list[int]] | None = None,
) -> bool:
    """Verifica se um jogo já foi sorteado na modalidade."""
    df = load_dataset(lottery_key)
    return check_game(sorted(numbers), df, extra_values=extras)


def generate_unique_combination_games(lottery_key: str, n: int = 10):
    """Gera combinações inéditas com base no histórico da modalidade."""
    config = _config(lottery_key)
    df = load_dataset(lottery_key)
    return generate_unique_combinations(
        df,
        n_games=n,
        total_bolas=config.total_bolas,
        universo=config.universo,
        extra_fields=config.extra_fields,
    )


def health_info() -> dict:
    """Informações completas para GET /health."""
    return get_health_payload()
