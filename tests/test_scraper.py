"""Testes do scraper resiliente (retry, fallback, erros amigáveis)."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from loterias_core.scraper import (
    DataSource,
    ScraperError,
    _request_with_retry,
    download_lottery_data,
)


def _megasena_xlsx_bytes() -> bytes:
    df = pd.DataFrame(
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
    buf = BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()


def test_request_with_retry_succeeds_after_transient_failure():
    responses = [
        MagicMock(status_code=503, raise_for_status=MagicMock(
            side_effect=requests.HTTPError(response=MagicMock(status_code=503))
        )),
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


def test_download_lottery_data_fallback_from_static_to_portal():
    xlsx = _megasena_xlsx_bytes()
    portal_response = MagicMock(status_code=200, content=xlsx)
    portal_response.raise_for_status = MagicMock(return_value=None)

    def _get(url, **_kwargs):
        if "D_megasena.xlsx" in url:
            resp = MagicMock(status_code=404)
            resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
            return resp
        return portal_response

    with patch("loterias_core.scraper.requests.get", side_effect=_get):
        with patch("loterias_core.scraper.time.sleep"):
            df = download_lottery_data("megasena", source=DataSource.AUTO, max_retries=1)

    assert len(df) == 2
    assert "Bola1" in df.columns or "bola1" in [c.lower() for c in df.columns]


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
