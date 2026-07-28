"""Rotas de verificação de jogos."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from api.deps import resolve_lottery
from api.schemas import GameRequest, validate_game_against_config
from api.services import core
from loterias_core.lotteries import LotteryConfig

logger = logging.getLogger(__name__)
router = APIRouter(tags=["verify"])
legacy_router = APIRouter(tags=["verify"])


def _validation_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail=message,
        headers={"X-Error-Code": "VALIDATION_ERROR"},
    )


def _verify(lottery_key: str, game: GameRequest, config: LotteryConfig) -> dict:
    try:
        numbers, extras = validate_game_against_config(game.numbers, game.extras, config)
    except ValueError as exc:
        raise _validation_error(str(exc)) from exc

    try:
        found = core.verify_game(lottery_key, numbers, extras)
        return {
            "lottery_key": lottery_key,
            "name": config.name,
            "numbers": numbers,
            "extras": extras,
            "found": found,
            "message": "Jogo já foi sorteado" if found else "Jogo nunca foi sorteado",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Dataset não encontrado para {config.name}. "
                f"Atualize via POST /lotteries/{lottery_key}/dataset ou faça upload no Streamlit."
            ),
        ) from None
    except Exception as exc:
        logger.exception("Erro ao verificar jogo (%s)", lottery_key)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar jogo: {exc}",
        ) from exc


@router.post("/{lottery_key}/verify")
def verify(
    game: GameRequest,
    config: LotteryConfig = Depends(resolve_lottery),
):
    """Verifica se um jogo já foi sorteado na modalidade informada."""
    return _verify(config.key, game, config)


@legacy_router.post("/")
def verify_megasena(game: GameRequest):
    """Alias legado: verificação Mega-Sena (`POST /verify/`)."""
    config = resolve_lottery("megasena")
    return _verify(config.key, game, config)
