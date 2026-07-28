"""Testes da API FastAPI."""

from __future__ import annotations

import os
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Variáveis de ambiente antes de importar a app (limites baixos para testes)
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("RATE_LIMIT_DATASET", "2/minute")
os.environ.setdefault("RATE_LIMIT_FORECAST", "2/minute")
os.environ.setdefault("MAX_FORECAST_N", "100")

from api.config import get_settings
from api.main import app

get_settings.cache_clear()


@pytest.fixture
def client():
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_dataset(tmp_path, monkeypatch):
    csv_path = tmp_path / "megasena.csv"
    df = pd.DataFrame(
        {
            "concurso": [1, 2],
            "bola1": [1, 2],
            "bola2": [3, 4],
            "bola3": [5, 6],
            "bola4": [7, 8],
            "bola5": [9, 10],
            "bola6": [11, 12],
            "jogo": [[1, 3, 5, 7, 9, 11], [2, 4, 6, 8, 10, 12]],
        }
    )
    df.to_csv(csv_path, index=False)
    monkeypatch.setattr("api.services.core.DATASET_PATH", str(csv_path))
    return csv_path


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "dataset" in body
    assert body["dataset"]["exists"] is False


def test_health_with_dataset(client, sample_dataset):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["dataset"]["exists"] is True
    assert body["dataset"]["total_records"] == 2
    assert body["dataset"]["last_update"] is not None


def test_verify_invalid_payload_returns_422(client, sample_dataset):
    response = client.post("/verify/", json={"numbers": [1, 2, 3]})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "detail" in body
    assert "numbers" in body["detail"].lower() or "6" in body["detail"]


def test_verify_out_of_range_returns_422(client, sample_dataset):
    response = client.post("/verify/", json={"numbers": [0, 1, 2, 3, 4, 5]})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"


def test_verify_duplicate_numbers_returns_422(client, sample_dataset):
    response = client.post("/verify/", json={"numbers": [1, 1, 2, 3, 4, 5]})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"


def test_verify_existing_game(client, sample_dataset):
    response = client.post("/verify/", json={"numbers": [1, 3, 5, 7, 9, 11]})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["numbers"] == [1, 3, 5, 7, 9, 11]


def test_verify_new_game(client, sample_dataset):
    response = client.post("/verify/", json={"numbers": [7, 14, 21, 28, 35, 42]})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is False


def test_verify_dataset_missing_returns_404(client, tmp_path, monkeypatch):
    monkeypatch.setattr("api.services.core.DATASET_PATH", str(tmp_path / "missing.csv"))
    response = client.post("/verify/", json={"numbers": [1, 2, 3, 4, 5, 6]})
    assert response.status_code == 404


def test_forecast_n_above_max_returns_422(client, sample_dataset):
    response = client.get("/forecast/?n=101")
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "101" in body["detail"] or "100" in body["detail"]


def test_forecast_n_zero_returns_422(client, sample_dataset):
    response = client.get("/forecast/?n=0")
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"


def test_forecast_success(client, sample_dataset):
    response = client.get("/forecast/?n=3")
    assert response.status_code == 200
    body = response.json()
    assert body["n_games"] == 3
    assert len(body["games"]) == 3
    for game in body["games"]:
        assert len(game["dezenas"]) == 6
        assert game["dezenas"] == sorted(game["dezenas"])


def test_forecast_dataset_missing_returns_404(client, tmp_path, monkeypatch):
    monkeypatch.setattr("api.services.core.DATASET_PATH", str(tmp_path / "missing.csv"))
    response = client.get("/forecast/?n=1")
    assert response.status_code == 404


def test_get_dataset_missing_returns_404(client, tmp_path, monkeypatch):
    monkeypatch.setattr("api.services.core.DATASET_PATH", str(tmp_path / "missing.csv"))
    response = client.get("/dataset/")
    assert response.status_code == 404


def test_get_dataset_success(client, sample_dataset):
    response = client.get("/dataset/")
    assert response.status_code == 200
    body = response.json()
    assert body["total_records"] == 2
    assert "jogo" in body["columns"]
    assert body["last_update"] is not None


@patch("api.routes.dataset.update_dataset")
def test_post_dataset_updates_with_mocked_scrape(
    mock_update, client, sample_dataset, megasena_fixture
):
    raw = pd.read_excel(megasena_fixture)
    mock_update.return_value = raw.assign(
        jogo=raw.apply(
            lambda r: sorted([r[f"Bola{i}"] for i in range(1, 7)]),
            axis=1,
        )
    )
    response = client.post("/dataset/")
    assert response.status_code == 200
    body = response.json()
    assert "atualizado" in body["message"].lower()
    assert body["total_records"] == 2
    mock_update.assert_called_once()


@patch("api.routes.dataset.update_dataset")
def test_post_dataset_scrape_error_returns_500(mock_update, client, sample_dataset):
    mock_update.side_effect = RuntimeError("scrape falhou")
    response = client.post("/dataset/")
    assert response.status_code == 500


@patch("api.routes.dataset.update_dataset")
def test_rate_limit_dataset(mock_update, client, sample_dataset):
    mock_update.return_value = pd.DataFrame({"jogo": [[1, 2, 3, 4, 5, 6]]})

    first = client.post("/dataset/")
    second = client.post("/dataset/")
    third = client.post("/dataset/")

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json()["code"] == "RATE_LIMIT_EXCEEDED"


@patch("api.routes.forecast.load_dataset")
@patch("api.routes.forecast.generate_unique_combinations")
def test_rate_limit_forecast(mock_generate, mock_load, client, sample_dataset):
    mock_load.return_value = pd.DataFrame({"jogo": [[1, 2, 3, 4, 5, 6]]})
    mock_generate.return_value = [{"dezenas": [1, 2, 3, 4, 5, 6], "extras": None}]

    responses = [client.get("/forecast/?n=1") for _ in range(3)]

    assert responses[0].status_code == 200
    assert responses[1].status_code == 200
    assert responses[2].status_code == 429
    assert responses[2].json()["code"] == "RATE_LIMIT_EXCEEDED"
