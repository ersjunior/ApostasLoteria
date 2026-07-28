from __future__ import annotations

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request

from api.config import get_settings
from api.limiter import limiter
from api.services import core
from api.services.core import get_dataset_status, load_dataset, update_dataset

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def get_dataset_info():
    """
    Retorna informações sobre o dataset Mega-Sena (CSV).
    """
    status = get_dataset_status()
    if not status["exists"]:
        raise HTTPException(
            status_code=404,
            detail="Dataset não encontrado. Use POST /dataset para criar/atualizar.",
        )
    try:
        df = load_dataset()
        return {
            "total_records": len(df),
            "columns": list(df.columns),
            "last_update": status["last_update"],
        }
    except Exception as exc:
        logger.exception("Erro ao carregar dataset")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar dataset: {exc}",
        ) from exc


@router.post("/")
@limiter.limit(get_settings().rate_limit_dataset)
def update_dataset_endpoint(request: Request):
    """
    Atualiza o dataset baixando os dados mais recentes da Caixa Econômica Federal.
    """
    del request  # exigido pelo slowapi
    logger.info("Iniciando scrape do dataset Mega-Sena (POST /dataset/)")
    started_at = datetime.now(tz=UTC)
    try:
        df = update_dataset()
        elapsed = (datetime.now(tz=UTC) - started_at).total_seconds()
        logger.info(
            "Scrape concluído com sucesso em %.1fs — %d registros gravados",
            elapsed,
            len(df),
        )
        status = get_dataset_status()
        return {
            "message": "Dataset atualizado com sucesso",
            "total_records": len(df),
            "columns": list(df.columns),
            "last_update": status["last_update"],
        }
    except Exception as exc:
        logger.exception("Erro ao atualizar dataset via scrape")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar dataset: {exc}",
        ) from exc
