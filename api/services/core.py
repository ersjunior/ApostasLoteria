"""Serviços core da API — delegam ao pacote loterias_core."""

from __future__ import annotations

import logging
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from loterias_core.generator import generate_unique_combinations
from loterias_core.lotteries import LOTTERIES_BY_KEY
from loterias_core.schema import DatasetSchemaError
from loterias_core.scraper import DataSource, ScraperError, download_lottery_data
from loterias_core.validator import check_game

logger = logging.getLogger(__name__)

DATASET_PATH = "app/data/megasena.csv"
MEGASENA_CONFIG = LOTTERIES_BY_KEY["megasena"].to_dict()


def _atomic_write_csv(df: pd.DataFrame, file_path: str) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".csv", dir=path.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        df.to_csv(tmp_path, index=False)
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def get_dataset_status() -> dict:
    """Metadados do CSV da Mega-Sena para /health e GET /dataset/."""
    path = Path(DATASET_PATH)
    if not path.exists():
        return {
            "exists": False,
            "path": DATASET_PATH,
            "last_update": None,
            "total_records": None,
        }

    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
    try:
        df = pd.read_csv(path)
        total_records = len(df)
    except Exception:
        logger.exception("Falha ao ler metadados do dataset em %s", DATASET_PATH)
        total_records = None

    return {
        "exists": True,
        "path": DATASET_PATH,
        "last_update": mtime,
        "total_records": total_records,
    }


def load_dataset():
    """Carrega o dataset da Mega-Sena (CSV legado da API)."""
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset não encontrado em {DATASET_PATH}. Por favor, atualize o dataset primeiro."
        )
    return pd.read_csv(DATASET_PATH)


def update_dataset(source: DataSource | str = DataSource.AUTO):
    """Atualiza o dataset baixando a versão mais recente com scraper resiliente."""
    logger.info("Iniciando download da base Mega-Sena (source=%s)", source)
    try:
        df_raw = download_lottery_data("megasena", source=source)
    except ScraperError as exc:
        logger.exception("Scraper falhou ao baixar Mega-Sena")
        raise RuntimeError(str(exc)) from exc

    df = df_raw.copy()
    df.columns = [c.lower().strip().replace(" ", "").replace("_", "") for c in df.columns]

    dezenas = [f"bola{i}" for i in range(1, 7)]
    missing = [c for c in dezenas if c not in df.columns]
    if missing:
        raise DatasetSchemaError(f"Base baixada sem colunas esperadas da Mega-Sena: {missing}")

    df["jogo"] = df[dezenas].apply(
        lambda row: sorted(int(v) for v in row.tolist() if str(v).strip().isdigit()),
        axis=1,
    )
    df = df[df["jogo"].apply(len) == 6]

    _atomic_write_csv(df, DATASET_PATH)
    logger.info("Dataset Mega-Sena persistido em %s (%d registros)", DATASET_PATH, len(df))
    return df


def verify_game(numbers: list[int]) -> bool:
    """Verifica se um jogo já foi sorteado."""
    df = load_dataset()
    return check_game(sorted(numbers), df)


def generate_unique_combination_games(n: int = 10):
    """Gera combinações inéditas com base no histórico da Mega-Sena."""
    df = load_dataset()
    return generate_unique_combinations(df, n_games=n, total_bolas=6, universo=60)
