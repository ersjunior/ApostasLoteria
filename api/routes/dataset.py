"""Rotas de consulta e atualização de dataset."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request

from api.config import get_settings
from api.deps import resolve_lottery
from api.limiter import limiter
from api.services import core
from api.services.core import update_dataset
from loterias_core.lotteries import LotteryConfig

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dataset"])
legacy_router = APIRouter(tags=["dataset"])


def _get_info(lottery_key: str, config: LotteryConfig) -> dict:
    status = core.get_dataset_status(lottery_key)
    if not status["exists"]:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Dataset não encontrado para {config.name}. "
                f"Use POST /lotteries/{lottery_key}/dataset."
            ),
        )
    try:
        df = core.load_dataset(lottery_key)
        return {
            "lottery_key": lottery_key,
            "name": config.name,
            "total_records": len(df),
            "columns": list(df.columns),
            "last_update": status["last_update"],
        }
    except Exception as exc:
        logger.exception("Erro ao carregar dataset (%s)", lottery_key)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar dataset: {exc}",
        ) from exc


def _update(lottery_key: str, config: LotteryConfig) -> dict:
    logger.info("Iniciando scrape do dataset %s", config.name)
    started_at = datetime.now(tz=UTC)
    try:
        df = update_dataset(lottery_key)
        elapsed = (datetime.now(tz=UTC) - started_at).total_seconds()
        logger.info(
            "Scrape %s concluído em %.1fs — %d registros",
            config.name,
            elapsed,
            len(df),
        )
        status = core.get_dataset_status(lottery_key)
        return {
            "lottery_key": lottery_key,
            "name": config.name,
            "message": "Dataset atualizado com sucesso",
            "total_records": len(df),
            "columns": list(df.columns),
            "last_update": status["last_update"],
        }
    except Exception as exc:
        logger.exception("Erro ao atualizar dataset via scrape (%s)", lottery_key)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar dataset: {exc}",
        ) from exc


@router.get("/{lottery_key}/dataset")
def get_dataset_info(config: LotteryConfig = Depends(resolve_lottery)):
    """Retorna informações sobre o dataset da modalidade no SQLite."""
    return _get_info(config.key, config)


@router.post("/{lottery_key}/dataset")
@limiter.limit(get_settings().rate_limit_dataset)
def update_dataset_endpoint(
    request: Request,
    config: LotteryConfig = Depends(resolve_lottery),
):
    """Baixa dados oficiais da Caixa e atualiza a modalidade no SQLite."""
    del request
    return _update(config.key, config)


@legacy_router.get("/")
def get_dataset_info_megasena():
    """Alias legado: info Mega-Sena (`GET /dataset/`)."""
    config = resolve_lottery("megasena")
    return _get_info(config.key, config)


@legacy_router.post("/")
@limiter.limit(get_settings().rate_limit_dataset)
def update_dataset_endpoint_megasena(request: Request):
    """Alias legado: atualiza Mega-Sena (`POST /dataset/`)."""
    del request
    config = resolve_lottery("megasena")
    return _update(config.key, config)
