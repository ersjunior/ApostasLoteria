"""Rota de geração de combinações inéditas (forecast)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from api.config import get_settings
from api.limiter import limiter
from api.schemas import NGamesQuery, n_games_query
from api.services.core import load_dataset
from loterias_core.generator import generate_unique_combinations

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
@limiter.limit(get_settings().rate_limit_forecast)
def forecast(
    request: Request,
    query: NGamesQuery = Depends(n_games_query),
):
    """
    Gera jogos da Mega-Sena que ainda não apareceram no histórico (combinações inéditas).
    """
    del request  # exigido pelo slowapi
    try:
        df = load_dataset()
        games = generate_unique_combinations(
            df,
            n_games=query.n,
            total_bolas=6,
            universo=60,
        )
        return {
            "n_games": query.n,
            "games": games,
            "message": "Jogos inéditos gerados com sucesso",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dataset não encontrado. Por favor, atualize o dataset primeiro (POST /dataset/).",
        ) from None
    except Exception as exc:
        logger.exception("Erro ao gerar forecast")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar jogos: {exc}",
        ) from exc
