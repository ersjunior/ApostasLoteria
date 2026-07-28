"""Testes de validação de schema e persistência atômica de datasets."""

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from loterias_core.dataset import atomic_write_excel, normalize_columns, persist_dataset
from loterias_core.lotteries import LOTTERIES_BY_KEY
from loterias_core.schema import DatasetSchemaError, validate_dataset_schema


MEGASENA_CONFIG = LOTTERIES_BY_KEY["megasena"].to_dict()


def _valid_megasena_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Concurso": [1, 2],
            "Bola1": [1, 10],
            "Bola2": [2, 20],
            "Bola3": [3, 30],
            "Bola4": [4, 40],
            "Bola5": [5, 50],
            "Bola6": [6, 60],
        }
    )


def _invalid_megasena_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Concurso": [1],
            "Bola1": [1],
            "Bola2": [2],
            "Bola3": [3],
            # faltam colunas de dezenas
        }
    )


def test_validate_dataset_schema_rejects_invalid_columns():
    df = normalize_columns(_invalid_megasena_df())
    with pytest.raises(DatasetSchemaError, match="Schema inválido"):
        validate_dataset_schema(df, MEGASENA_CONFIG, lottery_name="Mega-Sena")


def test_validate_dataset_schema_accepts_valid_file():
    df = normalize_columns(_valid_megasena_df())
    validate_dataset_schema(df, MEGASENA_CONFIG, lottery_name="Mega-Sena")


def test_persist_dataset_rejects_invalid_without_touching_existing(tmp_path):
    existing_path = tmp_path / "megasena.xlsx"
    existing = pd.DataFrame({"jogo": [[1, 2, 3, 4, 5, 6]]})
    existing.to_excel(existing_path, index=False)

    config = {**MEGASENA_CONFIG, "file_path": str(existing_path)}
    before = existing_path.read_bytes()

    with pytest.raises(DatasetSchemaError):
        persist_dataset(_invalid_megasena_df(), config, lottery_name="Mega-Sena")

    assert existing_path.read_bytes() == before


def test_persist_dataset_saves_valid_file(tmp_path):
    target = tmp_path / "megasena.xlsx"
    config = {**MEGASENA_CONFIG, "file_path": str(target)}

    result = persist_dataset(_valid_megasena_df(), config, lottery_name="Mega-Sena")

    assert target.exists()
    assert "jogo" in result.columns
    saved = pd.read_excel(target)
    assert len(saved) == 2
    assert "jogo" in saved.columns


def test_atomic_write_does_not_corrupt_on_failure(tmp_path):
    target = tmp_path / "out.xlsx"
    df = _valid_megasena_df()

    atomic_write_excel(df, str(target))
    original = target.read_bytes()

    with patch.object(pd.DataFrame, "to_excel", side_effect=RuntimeError("disk full")):
        with pytest.raises(RuntimeError, match="disk full"):
            atomic_write_excel(df, str(target))

    assert target.read_bytes() == original
    leftovers = list(tmp_path.glob("*.xlsx"))
    assert len(leftovers) == 1
