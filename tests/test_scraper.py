"""Testes do scraper resiliente (retry, fallback, erros amigáveis)."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from loterias_core.lotteries import LOTTERIES_BY_KEY
from loterias_core.scraper import (
    DataSource,
    ScraperError,
    _json_row_to_record,
    _parse_xlsx_content,
    _request_with_retry,
    download_lottery_data,
)
from tests.fixtures.factory import megasena_xlsx_bytes


def test_request_with_retry_succeeds_after_transient_failure():
    responses = [
        MagicMock(
            status_code=503,
            raise_for_status=MagicMock(
                side_effect=requests.HTTPError(response=MagicMock(status_code=503))
            ),
        ),
        MagicMock(status_code=200, raise_for_status=MagicMock(return_value=None)),
    ]

    with patch("loterias_core.scraper.requests.get", side_effect=responses) as mock_get:
        with patch("loterias_core.scraper.time.sleep"):
            response = _request_with_retry(
                "https://example.com/test",
                max_retries=3,
                backoff_base=0.01,
            )

    assert response.status_code == 200
    assert mock_get.call_count == 2
    assert mock_get.call_args.kwargs["headers"]["User-Agent"].startswith("ApostasLoteria/")


def test_request_with_retry_raises_scraper_error_after_exhausting_retries():
    def _always_fail(*_args, **_kwargs):
        mock_resp = MagicMock(status_code=500)
        mock_resp.raise_for_status.side_effect = requests.HTTPError(response=mock_resp)
        return mock_resp

    with patch("loterias_core.scraper.requests.get", side_effect=_always_fail):
        with patch("loterias_core.scraper.time.sleep"):
            with pytest.raises(ScraperError, match="Todas as 3 tentativas falharam"):
                _request_with_retry("https://example.com/fail", max_retries=3, backoff_base=0.01)


def test_request_with_retry_recovers_from_timeout():
    ok = MagicMock(status_code=200)
    ok.raise_for_status = MagicMock(return_value=None)

    with patch(
        "loterias_core.scraper.requests.get",
        side_effect=[requests.Timeout("timeout"), ok],
    ):
        with patch("loterias_core.scraper.time.sleep"):
            response = _request_with_retry(
                "https://example.com/timeout", max_retries=2, backoff_base=0.01
            )

    assert response.status_code == 200


def test_request_with_retry_recovers_from_connection_error():
    ok = MagicMock(status_code=200)
    ok.raise_for_status = MagicMock(return_value=None)

    with (
        patch(
            "loterias_core.scraper.requests.get",
            side_effect=[requests.ConnectionError("offline"), ok],
        ),
        patch("loterias_core.scraper.time.sleep"),
    ):
        response = _request_with_retry("https://example.com/conn", max_retries=2, backoff_base=0.01)

    assert response.status_code == 200


def test_request_with_retry_stops_early_on_404():
    resp404 = MagicMock(status_code=404)
    resp404.raise_for_status.side_effect = requests.HTTPError(response=resp404)

    with patch("loterias_core.scraper.requests.get", return_value=resp404) as mock_get:
        with patch("loterias_core.scraper.time.sleep"):
            with pytest.raises(ScraperError):
                _request_with_retry("https://example.com/missing", max_retries=3, backoff_base=0.01)

    assert mock_get.call_count == 1


def test_parse_xlsx_content_rejects_invalid_bytes():
    with pytest.raises(ScraperError, match="não é um XLSX válido"):
        _parse_xlsx_content(b"not-an-xlsx", "teste")


def test_parse_xlsx_content_rejects_empty_dataframe():
    buf = BytesIO()
    pd.DataFrame().to_excel(buf, index=False)
    with pytest.raises(ScraperError, match="vazio"):
        _parse_xlsx_content(buf.getvalue(), "teste")


def test_download_lottery_data_fallback_from_static_to_portal():
    xlsx = megasena_xlsx_bytes()
    portal_response = MagicMock(status_code=200, content=xlsx)
    portal_response.raise_for_status = MagicMock(return_value=None)

    def _get(url, **_kwargs):
        if "D_megasena.xlsx" in url:
            resp = MagicMock(status_code=404)
            resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
            return resp
        if "download" in url:
            return portal_response
        resp = MagicMock(status_code=404)
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
        return resp

    with patch("loterias_core.scraper.requests.get", side_effect=_get):
        with patch("loterias_core.scraper.time.sleep"):
            df = download_lottery_data("megasena", source=DataSource.AUTO, max_retries=1)

    assert len(df) == 2
    assert "Bola1" in df.columns or "bola1" in [c.lower() for c in df.columns]


def test_download_lottery_data_xlsx_static_source():
    xlsx = megasena_xlsx_bytes()
    response = MagicMock(status_code=200, content=xlsx)
    response.raise_for_status = MagicMock(return_value=None)

    with patch("loterias_core.scraper.requests.get", return_value=response):
        with patch("loterias_core.scraper.time.sleep"):
            df = download_lottery_data("megasena", source=DataSource.XLSX_STATIC, max_retries=1)

    assert len(df) == 2


def test_download_lottery_data_raises_friendly_error_when_all_sources_fail():
    def _always_fail(*_args, **_kwargs):
        resp = MagicMock(status_code=503)
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
        return resp

    with patch("loterias_core.scraper.requests.get", side_effect=_always_fail):
        with patch("loterias_core.scraper.time.sleep"):
            with pytest.raises(ScraperError, match="upload manual"):
                download_lottery_data(
                    "megasena",
                    source=DataSource.XLSX_PORTAL,
                    max_retries=1,
                )


def test_download_lottery_data_unknown_key():
    with pytest.raises(ScraperError, match="Modalidade desconhecida"):
        download_lottery_data("loteria_inexistente")


def test_json_row_to_record_megasena():
    config = LOTTERIES_BY_KEY["megasena"]
    data = {
        "numero": 1,
        "dataApuracao": "2020-01-01",
        "listaDezenas": ["01", "02", "03", "04", "05", "06"],
    }
    record = _json_row_to_record(data, config)
    assert record["concurso"] == 1
    assert record["bola1"] == 1
    assert record["bola6"] == 6


def test_json_row_to_record_mais_milionaria():
    config = LOTTERIES_BY_KEY["mais_milionaria"]
    data = {
        "numero": 10,
        "listaDezenas": ["1", "2", "3", "4", "5", "6"],
        "trevosSorteados": ["1", "2"],
    }
    record = _json_row_to_record(data, config)
    assert record["trevo1"] == 1
    assert record["trevo2"] == 2


def test_download_json_portal_builds_dataframe():
    config = LOTTERIES_BY_KEY["megasena"]

    latest = MagicMock(status_code=200)
    latest.raise_for_status = MagicMock(return_value=None)
    latest.json.return_value = {"numero": 2}

    def _concurso_json():
        mock = MagicMock(status_code=200)
        mock.raise_for_status = MagicMock(return_value=None)
        mock.json.side_effect = [
            {"numero": 1, "listaDezenas": ["1", "2", "3", "4", "5", "6"]},
            {"numero": 2, "listaDezenas": ["7", "8", "9", "10", "11", "12"]},
        ]
        return mock

    concurso_mock = _concurso_json()

    with patch(
        "loterias_core.scraper._request_with_retry",
        side_effect=[latest, concurso_mock, concurso_mock],
    ):
        from loterias_core.scraper import _download_json_portal

        df = _download_json_portal(config, max_retries=1, backoff_base=0.01, timeout=5)

    assert len(df) == 2
    assert "bola1" in df.columns


def test_download_megasena_data_legacy_alias():
    xlsx = megasena_xlsx_bytes()
    response = MagicMock(status_code=200, content=xlsx)
    response.raise_for_status = MagicMock(return_value=None)

    with patch("loterias_core.scraper.requests.get", return_value=response):
        with patch("loterias_core.scraper.time.sleep"):
            from loterias_core.scraper import download_megasena_data

            df = download_megasena_data(source=DataSource.XLSX_STATIC, max_retries=1)

    assert len(df) == 2
