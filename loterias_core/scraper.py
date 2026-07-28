"""Download resiliente de bases oficiais da Caixa (XLSX estático, portal e JSON)."""

from __future__ import annotations

import logging
import time
from enum import Enum
from io import BytesIO
from typing import Any

import pandas as pd
import requests

from loterias_core.lotteries import LOTTERIES_BY_KEY, LotteryConfig

logger = logging.getLogger(__name__)

USER_AGENT = "ApostasLoteria/0.1 (+https://github.com; uso educacional)"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 1.5

STATIC_XLSX_BASE = "https://loterias.caixa.gov.br/loterias/_arquivos/loterias"
PORTAL_XLSX_URL = (
    "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download"
)
PORTAL_JSON_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api"

# URL legada — mantida para compatibilidade
STATIC_XLSX_URL = f"{STATIC_XLSX_BASE}/D_megasena.xlsx"


class DataSource(str, Enum):
    """Fonte de dados configurável, com fallback automático entre opções."""

    AUTO = "auto"
    XLSX_STATIC = "xlsx_static"
    XLSX_PORTAL = "xlsx_portal"
    JSON_PORTAL = "json_portal"


class ScraperError(RuntimeError):
    """Erro amigável de download — nunca expor exceções cruas ao usuário."""


def _friendly_network_message(lottery_name: str, detail: str) -> str:
    return (
        f"Não foi possível baixar a base da **{lottery_name}**.\n\n"
        f"{detail}\n\n"
        "➡️ Tente novamente em alguns minutos ou faça upload manual do XLSX oficial."
    )


def _request_with_retry(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
    params: dict[str, Any] | None = None,
) -> requests.Response:
    headers = {"User-Agent": USER_AGENT}
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                params=params,
            )
            response.raise_for_status()
            return response
        except requests.Timeout as exc:
            last_error = exc
            detail = f"Tempo esgotado ({timeout}s) na tentativa {attempt}/{max_retries}."
            logger.warning("Timeout ao acessar %s: %s", url, detail)
        except requests.ConnectionError as exc:
            last_error = exc
            detail = f"Falha de conexão na tentativa {attempt}/{max_retries}."
            logger.warning("ConnectionError ao acessar %s: %s", url, detail)
        except requests.HTTPError as exc:
            last_error = exc
            status = exc.response.status_code if exc.response is not None else "?"
            detail = f"HTTP {status} na tentativa {attempt}/{max_retries}."
            logger.warning("HTTPError ao acessar %s: %s", url, detail)
            if exc.response is not None and exc.response.status_code in (404, 403, 401):
                break
        except requests.RequestException as exc:
            last_error = exc
            detail = f"Erro de rede na tentativa {attempt}/{max_retries}."
            logger.warning("RequestException ao acessar %s: %s", url, exc)

        if attempt < max_retries:
            sleep_s = backoff_base ** (attempt - 1)
            time.sleep(sleep_s)

    raise ScraperError(
        _friendly_network_message(
            "Caixa",
            f"Todas as {max_retries} tentativas falharam ({last_error}).",
        )
    ) from last_error


def _parse_xlsx_content(content: bytes, source_label: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(BytesIO(content))
    except Exception as exc:
        raise ScraperError(
            f"O arquivo baixado via {source_label} não é um XLSX válido.\n\n"
            "➡️ Use o upload manual do XLSX oficial."
        ) from exc

    if df.empty:
        raise ScraperError(f"Arquivo XLSX vazio (fonte: {source_label}).")

    return df


def _download_xlsx_static(config: LotteryConfig, **request_kwargs: Any) -> pd.DataFrame:
    url = f"{STATIC_XLSX_BASE}/D_{config.key}.xlsx"
    response = _request_with_retry(url, **request_kwargs)
    return _parse_xlsx_content(response.content, "XLSX estático")


def _download_xlsx_portal(config: LotteryConfig, **request_kwargs: Any) -> pd.DataFrame:
    modalidade = config.portal_modalidade
    response = _request_with_retry(
        PORTAL_XLSX_URL,
        params={"modalidade": modalidade},
        timeout=max(request_kwargs.get("timeout", DEFAULT_TIMEOUT), 60.0),
        max_retries=request_kwargs.get("max_retries", DEFAULT_MAX_RETRIES),
        backoff_base=request_kwargs.get("backoff_base", DEFAULT_BACKOFF_BASE),
    )
    return _parse_xlsx_content(response.content, "portal da Caixa")


def _json_row_to_record(data: dict[str, Any], config: LotteryConfig) -> dict[str, Any]:
    record: dict[str, Any] = {
        "concurso": data.get("numero"),
        "datasorteio": data.get("dataApuracao"),
    }

    dezenas = data.get("listaDezenas") or []
    for i, val in enumerate(dezenas, start=1):
        record[f"bola{i}"] = int(str(val).strip())

    if config.multiple_draws:
        segundo = data.get("listaDezenasSegundoSorteio") or []
        for i, val in enumerate(segundo, start=1):
            record[f"bola{i}sorteio2"] = int(str(val).strip())
        for i in range(1, config.total_bolas + 1):
            key = f"bola{i}"
            if key in record:
                record[f"bola{i}sorteio1"] = record.pop(key)

    if config.special_handler == "mais_milionaria":
        trevos = data.get("trevosSorteados") or data.get("listaTrevos") or []
        for i, val in enumerate(trevos[:2], start=1):
            record[f"trevo{i}"] = int(str(val).strip())

    if config.extra_fields and "timecoração" in (config.extra_fields or {}):
        record["timecoração"] = data.get("nomeTimeCoracaoMesSorte") or ""

    return record


def _download_json_portal(config: LotteryConfig, **request_kwargs: Any) -> pd.DataFrame:
    """Baixa histórico via API JSON do portal (1 request por concurso)."""
    latest_url = f"{PORTAL_JSON_BASE}/{config.key}"
    latest_resp = _request_with_retry(latest_url, **request_kwargs)
    latest = latest_resp.json()
    max_concurso = int(latest["numero"])

    records: list[dict[str, Any]] = []
    timeout = request_kwargs.get("timeout", DEFAULT_TIMEOUT)
    max_retries = request_kwargs.get("max_retries", DEFAULT_MAX_RETRIES)
    backoff_base = request_kwargs.get("backoff_base", DEFAULT_BACKOFF_BASE)

    for numero in range(1, max_concurso + 1):
        url = f"{PORTAL_JSON_BASE}/{config.key}/{numero}"
        resp = _request_with_retry(
            url,
            timeout=timeout,
            max_retries=max_retries,
            backoff_base=backoff_base,
        )
        records.append(_json_row_to_record(resp.json(), config))

    df = pd.DataFrame(records)
    if df.empty:
        raise ScraperError("API JSON do portal não retornou concursos.")
    return df


_SOURCE_FETCHERS = {
    DataSource.XLSX_STATIC: _download_xlsx_static,
    DataSource.XLSX_PORTAL: _download_xlsx_portal,
    DataSource.JSON_PORTAL: _download_json_portal,
}


def download_lottery_data(
    lottery_key: str = "megasena",
    source: DataSource | str = DataSource.AUTO,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
) -> pd.DataFrame:
    """
    Baixa base oficial da loteria com retry, timeout e fallback entre fontes.
    """
    if lottery_key not in LOTTERIES_BY_KEY:
        raise ScraperError(f"Modalidade desconhecida: {lottery_key}")

    config = LOTTERIES_BY_KEY[lottery_key]
    if isinstance(source, str):
        source = DataSource(source)

    request_kwargs = {
        "timeout": timeout,
        "max_retries": max_retries,
        "backoff_base": backoff_base,
    }

    if source == DataSource.AUTO:
        chain = (DataSource.XLSX_PORTAL, DataSource.XLSX_STATIC, DataSource.JSON_PORTAL)
    else:
        chain = (source,)

    errors: list[str] = []

    for src in chain:
        fetcher = _SOURCE_FETCHERS[src]
        try:
            logger.info("Baixando %s via %s", config.name, src.value)
            return fetcher(config, **request_kwargs)
        except ScraperError as exc:
            errors.append(f"• {src.value}: {exc}")
            logger.warning("Fonte %s falhou para %s: %s", src.value, config.name, exc)

    raise ScraperError(
        _friendly_network_message(
            config.name,
            "Nenhuma fonte disponível funcionou:\n" + "\n".join(errors),
        )
    )


def download_megasena_data(
    source: DataSource | str = DataSource.AUTO,
    **kwargs: Any,
) -> pd.DataFrame:
    """Compatibilidade com código legado da API."""
    return download_lottery_data("megasena", source=source, **kwargs)
