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
from loterias_core.lotteries import LOTTERIES_BY_KEY

get_settings.cache_clear()


@pytest.fixture
def client():
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_dataset(sample_megasena_db):
    return sample_megasena_db


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "dataset" in body
    assert "lotteries" in body
    assert "database" in body
    assert body["dataset"]["exists"] is False


def test_health_with_dataset(client, sample_dataset):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["dataset"]["exists"] is True
    assert body["dataset"]["total_records"] == 2
    assert body["dataset"]["last_update"] is not None
    assert body["lotteries"]["megasena"]["exists"] is True


def test_list_lotteries(client):
    response = client.get("/lotteries")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == len(LOTTERIES_BY_KEY)
    keys = {item["key"] for item in body["lotteries"]}
    assert keys == set(LOTTERIES_BY_KEY)
    megasena = next(item for item in body["lotteries"] if item["key"] == "megasena")
    assert megasena["total_bolas"] == 6
    assert megasena["universo"] == 60


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
    response = client.post("/verify/", json={"numbers": [1, 2, 3, 4, 5, 6]})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["numbers"] == [1, 2, 3, 4, 5, 6]
    assert body["lottery_key"] == "megasena"


def test_verify_new_game(client, sample_dataset):
    response = client.post("/verify/", json={"numbers": [7, 14, 21, 28, 35, 42]})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is False


def test_verify_dataset_missing_returns_404(client):
    response = client.post("/verify/", json={"numbers": [1, 2, 3, 4, 5, 6]})
    assert response.status_code == 404


def test_verify_unknown_lottery_returns_404(client):
    response = client.post(
        "/lotteries/naoexiste/verify",
        json={"numbers": [1, 2, 3, 4, 5, 6]},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_verify_wrong_length_for_lottery_returns_422(client):
    response = client.post(
        "/lotteries/lotofacil/verify",
        json={"numbers": [1, 2, 3, 4, 5, 6]},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert "15" in response.json()["detail"]


@patch("api.routes.verify.core.verify_game", return_value=False)
def test_verify_lotofacil_path(mock_verify, client):
    numbers = list(range(1, 16))
    response = client.post(
        "/lotteries/lotofacil/verify",
        json={"numbers": numbers},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["lottery_key"] == "lotofacil"
    assert body["found"] is False
    mock_verify.assert_called_once()
    assert mock_verify.call_args.args[0] == "lotofacil"
    assert mock_verify.call_args.args[1] == numbers


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
    assert body["lottery_key"] == "megasena"
    assert len(body["games"]) == 3
    for game in body["games"]:
        assert len(game["dezenas"]) == 6
        assert game["dezenas"] == sorted(game["dezenas"])


def test_forecast_dataset_missing_returns_404(client):
    response = client.get("/forecast/?n=1")
    assert response.status_code == 404


@patch("api.routes.combinations.core.generate_unique_combination_games")
def test_combinations_quina_uses_config(mock_generate, client):
    mock_generate.return_value = [
        {"dezenas": [1, 2, 3, 4, 5], "extras": None},
        {"dezenas": [6, 7, 8, 9, 10], "extras": None},
    ]
    response = client.get("/lotteries/quina/combinations?n=2")
    assert response.status_code == 200
    body = response.json()
    assert body["lottery_key"] == "quina"
    assert body["n_games"] == 2
    mock_generate.assert_called_once_with("quina", n=2)


def test_get_dataset_missing_returns_404(client):
    response = client.get("/dataset/")
    assert response.status_code == 404


def test_get_dataset_success(client, sample_dataset):
    response = client.get("/dataset/")
    assert response.status_code == 200
    body = response.json()
    assert body["total_records"] == 2
    assert body["lottery_key"] == "megasena"
    assert "jogo" in body["columns"]
    assert body["last_update"] is not None


def test_get_dataset_path_megasena(client, sample_dataset):
    response = client.get("/lotteries/megasena/dataset")
    assert response.status_code == 200
    assert response.json()["lottery_key"] == "megasena"


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


@patch("api.routes.forecast.core.generate_unique_combination_games")
def test_rate_limit_forecast(mock_generate, client, sample_dataset):
    mock_generate.return_value = [{"dezenas": [1, 2, 3, 4, 5, 6], "extras": None}]

    responses = [client.get("/forecast/?n=1") for _ in range(3)]

    assert responses[0].status_code == 200
    assert responses[1].status_code == 200
    assert responses[2].status_code == 429
    assert responses[2].json()["code"] == "RATE_LIMIT_EXCEEDED"
