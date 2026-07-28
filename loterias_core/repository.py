"""Repositório de datasets — interface de alto nível sobre SQLite."""

from __future__ import annotations

from typing import Any

import pandas as pd

from loterias_core.storage import (
    get_all_lotteries_status,
    get_database_info,
    get_db_path,
    get_lottery_status,
    import_from_xlsx_path,
    init_db,
    load_draws,
    save_draws_full,
    save_draws_incremental,
)


def _config_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_bolas": config["total_bolas"],
        "extra_fields": config.get("extra_fields"),
        "multiple_draws": config.get("multiple_draws", False),
        "special_handler": config.get("special_handler"),
    }


def ensure_database() -> None:
    """Inicializa o banco se necessário."""
    init_db()


def lottery_has_data(lottery_key: str) -> bool:
    return get_lottery_status(lottery_key)["exists"]


def load_lottery_dataframe(lottery_key: str) -> pd.DataFrame:
    """Carrega DataFrame processado de uma modalidade."""
    records = load_draws(lottery_key)
    if not records:
        name = lottery_key
        raise FileNotFoundError(
            f"Dataset não encontrado para **{name}**.\n\n"
            "➡️ Faça upload do XLSX oficial na página inicial ou atualize via API."
        )
    return pd.DataFrame(records)


def persist_lottery_dataframe(
    lottery_key: str,
    df: pd.DataFrame,
    *,
    incremental: bool = False,
) -> int:
    """Persiste DataFrame processado (com coluna jogo)."""
    records = df.to_dict(orient="records")
    if incremental:
        return save_draws_incremental(lottery_key, records)
    return save_draws_full(lottery_key, records)


def import_xlsx_to_db(file_path: str, config: dict[str, Any]) -> int:
    """Importa arquivo XLSX oficial para o banco."""
    from loterias_core.dataset import load_dataset

    lottery_key = config["key"]
    return import_from_xlsx_path(
        file_path,
        lottery_key,
        loader=load_dataset,
        loader_kwargs=_config_kwargs(config),
    )


def update_lottery_from_raw(
    lottery_key: str,
    df_raw: pd.DataFrame,
    config: dict[str, Any],
    *,
    incremental: bool = True,
) -> tuple[pd.DataFrame, int]:
    """
    Processa DataFrame bruto (download Caixa) e persiste no banco.
    Retorna (DataFrame processado, quantidade de registros inseridos).
    """
    from loterias_core.dataset import process_raw_dataset

    processed = process_raw_dataset(df_raw, config)
    inserted = persist_lottery_dataframe(lottery_key, processed, incremental=incremental)
    return processed, inserted


def get_cache_status(lottery_key: str | None = None) -> dict[str, Any]:
    """Metadados de cache — uma modalidade ou todas."""
    if lottery_key:
        return get_lottery_status(lottery_key)
    return get_all_lotteries_status()


def get_health_payload() -> dict[str, Any]:
    """Payload completo para /health."""
    db_info = get_database_info()
    lotteries = get_all_lotteries_status()
    megasena = get_lottery_status("megasena")
    return {
        "database": db_info,
        "lotteries": lotteries,
        "dataset": {
            "exists": megasena["exists"],
            "path": get_db_path(),
            "last_update": megasena["last_update"],
            "last_concurso": megasena["last_concurso"],
            "total_records": megasena["total_records"] if megasena["exists"] else None,
        },
    }


__all__ = [
    "ensure_database",
    "get_cache_status",
    "get_health_payload",
    "import_xlsx_to_db",
    "load_lottery_dataframe",
    "lottery_has_data",
    "persist_lottery_dataframe",
    "update_lottery_from_raw",
]
