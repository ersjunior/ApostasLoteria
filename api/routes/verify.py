from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from api.schemas import GameRequest
from api.services.core import load_dataset
from loterias_core.validator import check_game

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/")
def verify(game: GameRequest):
    """
    Verifica se um jogo da Mega-Sena já foi sorteado.
    """
    try:
        df = load_dataset()
        numbers = sorted(game.numbers)
        found = check_game(numbers, df)

        return {
            "numbers": numbers,
            "found": found,
            "message": "Jogo já foi sorteado" if found else "Jogo nunca foi sorteado",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dataset não encontrado. Por favor, atualize o dataset primeiro.",
        ) from None
    except Exception as exc:
        logger.exception("Erro ao verificar jogo")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar jogo: {exc}",
        ) from exc
