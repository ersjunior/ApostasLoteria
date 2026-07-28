"""Testes de carga, persistência e atualização do dataset (rede mockada)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from loterias_core.dataset import (
    atomic_write_excel,
    enrich_dataset,
    load_dataset,
    normalize_columns,
    persist_dataset,
    process_raw_dataset,
    save_dataset,
)
from loterias_core.lotteries import LOTTERIES_BY_KEY
from loterias_core.schema import DatasetSchemaError


def test_normalize_columns_lowercases_and_strips():
    df = pd.DataFrame({" Bola 1 ": [1], "BOLA_2": [2]})
    result = normalize_columns(df)
    assert list(result.columns) == ["bola1", "bola2"]


def test_enrich_dataset_builds_jogo_column():
    df = pd.DataFrame(
        {
            "bola1": [1, 10],
            "bola2": [2, 20],
            "bola3": [3, 30],
            "bola4": [4, 40],
            "bola5": [5, 50],
            "bola6": [6, 60],
        }
    )
    enriched = enrich_dataset(df, total_bolas=6)
    assert "jogo" in enriched.columns
    assert enriched.iloc[0]["jogo"] == [1, 2, 3, 4, 5, 6]
    assert len(enriched) == 2


def test_enrich_dataset_rejects_missing_columns():
    df = pd.DataFrame({"bola1": [1]})
    with pytest.raises(ValueError, match="Colunas inválidas"):
        enrich_dataset(df, total_bolas=6)


def test_load_dataset_megasena(megasena_fixture):
    df = load_dataset(str(megasena_fixture), total_bolas=6)
    assert len(df) == 2
    assert all(len(j) == 6 for j in df["jogo"])


def test_load_dataset_lotofacil(lottery_fixture_paths):
    path = lottery_fixture_paths["lotofacil"]
    df = load_dataset(str(path), total_bolas=15)
    assert len(df) == 2
    assert all(len(j) == 15 for j in df["jogo"])


def test_load_dataset_quina(lottery_fixture_paths):
    path = lottery_fixture_paths["quina"]
    df = load_dataset(str(path), total_bolas=5)
    assert len(df) == 2
    assert all(len(j) == 5 for j in df["jogo"])


def test_load_dataset_duplasena_multiple_draws(lottery_fixture_paths):
    path = lottery_fixture_paths["duplasena"]
    df = load_dataset(str(path), total_bolas=6, multiple_draws=True)
    assert len(df) == 4  # 2 concursos × 2 sorteios
    assert all(len(j) == 6 for j in df["jogo"])


def test_load_dataset_lotomania_special_handler(lottery_fixture_paths):
    path = lottery_fixture_paths["lotomania"]
    raw = pd.read_excel(path, dtype=str)
    with patch("loterias_core.dataset.pd.read_excel", return_value=raw):
        df = load_dataset(str(path), total_bolas=50, special_handler="lotomania")
    assert len(df) == 2
    assert all(len(j) == 50 for j in df["jogo"])


def test_load_dataset_supersete_special_handler(lottery_fixture_paths):
    path = lottery_fixture_paths["supersete"]
    df = load_dataset(str(path), total_bolas=7, special_handler="supersete")
    assert len(df) == 2
    assert all(len(j) == 7 for j in df["jogo"])


def test_load_dataset_mais_milionaria_special_handler(lottery_fixture_paths):
    path = lottery_fixture_paths["mais_milionaria"]
    df = load_dataset(str(path), total_bolas=6, special_handler="mais_milionaria")
    assert len(df) == 2
    assert "trevos" in df.columns
    assert all(len(row["trevos"]) == 2 for _, row in df.iterrows())


def test_load_dataset_file_not_found():
    with pytest.raises(FileNotFoundError, match="Dataset não encontrado"):
        load_dataset("inexistente.xlsx", total_bolas=6)


def test_atomic_write_excel_creates_file(tmp_path):
    df = pd.DataFrame({"bola1": [1], "jogo": [[1]]})
    target = tmp_path / "subdir" / "out.xlsx"
    atomic_write_excel(df, str(target))
    assert target.exists()
    loaded = pd.read_excel(target)
    assert len(loaded) == 1


def test_save_dataset_persists_and_enriches(megasena_fixture, tmp_path):
    raw = pd.read_excel(megasena_fixture)
    out = tmp_path / "saved.xlsx"
    save_dataset(raw, str(out), total_bolas=6)
    assert out.exists()
    loaded = load_dataset(str(out), total_bolas=6)
    assert "jogo" in loaded.columns
    assert len(loaded) == 2


def test_persist_dataset_validates_and_writes(megasena_fixture, megasena_config, tmp_path):
    megasena_config["file_path"] = str(tmp_path / "persisted.xlsx")
    raw = pd.read_excel(megasena_fixture)
    result = persist_dataset(raw, megasena_config, lottery_name="Mega-Sena")
    assert len(result) == 2
    assert Path(megasena_config["file_path"]).exists()


def test_persist_dataset_invalid_schema_raises(megasena_config, tmp_path):
    megasena_config["file_path"] = str(tmp_path / "bad.xlsx")
    raw = pd.DataFrame({"coluna_errada": [1]})
    with pytest.raises(DatasetSchemaError):
        persist_dataset(raw, megasena_config)


def test_process_raw_dataset_from_dataframe(megasena_fixture, megasena_config):
    raw = pd.read_excel(megasena_fixture)
    processed = process_raw_dataset(raw, megasena_config)
    assert len(processed) == 2
    assert "jogo" in processed.columns


@patch("api.services.core.download_lottery_data")
def test_update_dataset_persists_csv(mock_download, megasena_fixture, tmp_path, monkeypatch):
    import api.services.core as core

    raw = pd.read_excel(megasena_fixture)
    mock_download.return_value = raw
    csv_path = tmp_path / "megasena.csv"
    monkeypatch.setattr(core, "DATASET_PATH", str(csv_path))

    df = core.update_dataset()
    assert len(df) == 2
    assert csv_path.exists()
    assert "jogo" in df.columns
    mock_download.assert_called_once()


@patch("api.services.core.download_lottery_data")
def test_update_dataset_scraper_error(mock_download, tmp_path, monkeypatch):
    import api.services.core as core

    from loterias_core.scraper import ScraperError

    mock_download.side_effect = ScraperError("falha simulada")
    monkeypatch.setattr(core, "DATASET_PATH", str(tmp_path / "megasena.csv"))

    with pytest.raises(RuntimeError, match="falha simulada"):
        core.update_dataset()


def test_get_dataset_status_missing(tmp_path, monkeypatch):
    import api.services.core as core

    monkeypatch.setattr(core, "DATASET_PATH", str(tmp_path / "missing.csv"))
    status = core.get_dataset_status()
    assert status["exists"] is False
    assert status["total_records"] is None


def test_get_dataset_status_with_csv(megasena_csv_fixture, monkeypatch):
    import api.services.core as core

    monkeypatch.setattr(core, "DATASET_PATH", str(megasena_csv_fixture))
    status = core.get_dataset_status()
    assert status["exists"] is True
    assert status["total_records"] == 2
    assert status["last_update"] is not None


def test_load_dataset_api_csv(megasena_csv_fixture, monkeypatch):
    import api.services.core as core

    monkeypatch.setattr(core, "DATASET_PATH", str(megasena_csv_fixture))
    df = core.load_dataset()
    assert len(df) == 2


def test_load_dataset_api_missing_raises(tmp_path, monkeypatch):
    import api.services.core as core

    monkeypatch.setattr(core, "DATASET_PATH", str(tmp_path / "missing.csv"))
    with pytest.raises(FileNotFoundError):
        core.load_dataset()


def test_timemania_extra_field(lottery_fixture_paths):
    path = lottery_fixture_paths["timemania"]
    config = LOTTERIES_BY_KEY["timemania"].to_dict()
    raw = pd.read_excel(path)
    processed = process_raw_dataset(raw, config)
    assert "timecoração" in processed.columns or "timecoracao" in processed.columns
