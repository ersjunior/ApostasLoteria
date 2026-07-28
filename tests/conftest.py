"""Fixtures compartilhadas — datasets sintéticos e seeds determinísticos."""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd
import pytest

from loterias_core.lotteries import LOTTERIES_BY_KEY
from tests.fixtures.factory import FIXTURES_DIR, build_all_fixtures


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Isola testes de rate limit — slowapi acumula contagem entre chamadas."""
    from api.limiter import limiter

    storage = getattr(limiter, "_storage", None)
    inner = getattr(storage, "storage", None) if storage is not None else None
    if isinstance(inner, dict):
        inner.clear()
    yield
    if isinstance(inner, dict):
        inner.clear()


@pytest.fixture(autouse=True)
def fixed_random_seed():
    """Garante reprodutibilidade nos geradores com aleatoriedade."""
    random.seed(42)
    yield
    random.seed(None)


@pytest.fixture(scope="session")
def lottery_fixture_paths() -> dict[str, Path]:
    """Arquivos XLSX/CSV sintéticos por modalidade (sem rede)."""
    return build_all_fixtures()


@pytest.fixture
def megasena_fixture(lottery_fixture_paths) -> Path:
    return lottery_fixture_paths["megasena"]


@pytest.fixture
def megasena_csv_fixture(lottery_fixture_paths) -> Path:
    return lottery_fixture_paths["megasena_csv"]


@pytest.fixture
def megasena_config() -> dict:
    cfg = LOTTERIES_BY_KEY["megasena"].to_dict()
    return {**cfg, "file_path": str(FIXTURES_DIR / "megasena_out.xlsx")}


@pytest.fixture
def sample_megasena_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "concurso": [1, 2, 3],
            "bola1": [1, 10, 5],
            "bola2": [2, 20, 15],
            "bola3": [3, 30, 25],
            "bola4": [4, 40, 35],
            "bola5": [5, 50, 45],
            "bola6": [6, 60, 55],
            "jogo": [
                [1, 2, 3, 4, 5, 6],
                [10, 20, 30, 40, 50, 60],
                [5, 15, 25, 35, 45, 55],
            ],
        }
    )
