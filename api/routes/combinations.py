"""Rotas de geração de combinações inéditas."""

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
router = APIRouter(tags=["combinations"])
legacy_router = APIRouter(tags=["combinations"])


def _generate(lottery_key: str, config: LotteryConfig, n: int) -> dict:
    try:
        games = core.generate_unique_combination_games(lottery_key, n=n)
        return {
            "lottery_key": lottery_key,
            "name": config.name,
            "n_games": n,
            "games": games,
            "message": "Combinações inéditas geradas com sucesso",
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
        logger.exception("Erro ao gerar combinações (%s)", lottery_key)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar combinações: {exc}",
        ) from exc


@router.get("/{lottery_key}/combinations")
@limiter.limit(get_settings().rate_limit_combinations)
def generate_combinations(
    request: Request,
    config: LotteryConfig = Depends(resolve_lottery),
    query: NGamesQuery = Depends(n_games_query),
):
    """Gera combinações inéditas por sorteio aleatório (sem modelo preditivo)."""
    del request
    return _generate(config.key, config, query.n)


@legacy_router.get("/")
@limiter.limit(get_settings().rate_limit_combinations)
def generate_combinations_megasena(
    request: Request,
    query: NGamesQuery = Depends(n_games_query),
):
    """Alias legado: combinações Mega-Sena (`GET /combinations/`)."""
    del request
    config = resolve_lottery("megasena")
    return _generate(config.key, config, query.n)
