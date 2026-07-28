"""Testes de persistência SQLite e cache incremental por loteria."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from loterias_core.repository import (
    get_cache_status,
    load_lottery_dataframe,
    persist_lottery_dataframe,
    update_lottery_from_raw,
)
from loterias_core.storage import get_lottery_status, init_db, save_draws_incremental


def test_init_db_creates_tables(db_path):
    init_db(str(db_path))
    assert db_path.exists()


def test_persist_and_load_lottery(megasena_fixture, megasena_config):
    raw = pd.read_excel(megasena_fixture)
    processed, _ = update_lottery_from_raw("megasena", raw, megasena_config, incremental=False)
    assert len(processed) == 2

    df = load_lottery_dataframe("megasena")
    assert len(df) == 2
    assert "jogo" in df.columns

    status = get_lottery_status("megasena")
    assert status["exists"] is True
    assert status["total_records"] == 2
    assert status["last_concurso"] == 2


def test_incremental_update_skips_existing(megasena_fixture, megasena_config):
    raw = pd.read_excel(megasena_fixture)
    update_lottery_from_raw("megasena", raw, megasena_config, incremental=False)

    records = [
        {"concurso": 1, "jogo": [1, 2, 3, 4, 5, 6]},
        {"concurso": 2, "jogo": [10, 20, 30, 40, 50, 60]},
    ]
    inserted = save_draws_incremental("megasena", records)
    assert inserted == 0
    assert get_lottery_status("megasena")["total_records"] == 2


def test_incremental_update_adds_new_concurso(megasena_config):
    base = pd.DataFrame(
        {
            "concurso": [1],
            "bola1": [1],
            "bola2": [2],
            "bola3": [3],
            "bola4": [4],
            "bola5": [5],
            "bola6": [6],
        }
    )
    update_lottery_from_raw("megasena", base, megasena_config, incremental=False)

    extended = pd.DataFrame(
        {
            "concurso": [1, 2],
            "bola1": [1, 10],
            "bola2": [2, 20],
            "bola3": [3, 30],
            "bola4": [4, 40],
            "bola5": [5, 50],
            "bola6": [6, 60],
        }
    )
    _, inserted = update_lottery_from_raw("megasena", extended, megasena_config, incremental=True)
    assert inserted == 1
    assert get_lottery_status("megasena")["total_records"] == 2
    assert get_lottery_status("megasena")["last_concurso"] == 2


def test_get_cache_status_all_lotteries(sample_megasena_db):
    all_status = get_cache_status()
    assert "megasena" in all_status
    assert all_status["megasena"]["exists"] is True


def test_load_missing_lottery_raises():
    with pytest.raises(FileNotFoundError, match="Dataset não encontrado"):
        load_lottery_dataframe("quina")


def test_persist_dataframe_direct():
    df = pd.DataFrame({"concurso": [1], "jogo": [[1, 2, 3, 4, 5, 6]]})
    total = persist_lottery_dataframe("megasena", df)
    assert total == 1


@patch("api.services.core.download_lottery_data")
def test_api_update_dataset_sqlite(mock_download, megasena_fixture, megasena_config):
    import api.services.core as core

    mock_download.return_value = pd.read_excel(megasena_fixture)
    df = core.update_dataset()
    assert len(df) == 2
    status = core.get_dataset_status()
    assert status["exists"] is True
    assert status["total_records"] == 2
