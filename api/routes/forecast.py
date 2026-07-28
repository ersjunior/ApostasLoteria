"""Rota de geração de combinações inéditas (forecast — alias semântico)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from api.config import get_settings
from api.deps import resolve_lottery
from api.limiter import limiter
from api.schemas import NGamesQuery, n_games_query
from api.services import core
from loterias_core.lotteries import LotteryConfig

logger = logging.getLogger(__name__)
router = APIRouter(tags=["forecast"])
legacy_router = APIRouter(tags=["forecast"])


def _forecast(lottery_key: str, config: LotteryConfig, n: int) -> dict:
    try:
        games = core.generate_unique_combination_games(lottery_key, n=n)
        return {
            "lottery_key": lottery_key,
            "name": config.name,
            "n_games": n,
            "games": games,
            "message": "Jogos inéditos gerados com sucesso",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Dataset não encontrado para {config.name}. "
                f"Atualize via POST /lotteries/{lottery_key}/dataset."
            ),
        ) from None
    except Exception as exc:
        logger.exception("Erro ao gerar forecast (%s)", lottery_key)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar jogos: {exc}",
        ) from exc


@router.get("/{lottery_key}/forecast")
@limiter.limit(get_settings().rate_limit_forecast)
def forecast(
    request: Request,
    config: LotteryConfig = Depends(resolve_lottery),
    query: NGamesQuery = Depends(n_games_query),
):
    """Gera jogos inéditos da modalidade (mesmo domínio de /combinations)."""
    del request
    return _forecast(config.key, config, query.n)


@legacy_router.get("/")
@limiter.limit(get_settings().rate_limit_forecast)
def forecast_megasena(
    request: Request,
    query: NGamesQuery = Depends(n_games_query),
):
    """Alias legado: forecast Mega-Sena (`GET /forecast/`)."""
    del request
    config = resolve_lottery("megasena")
    return _forecast(config.key, config, query.n)
