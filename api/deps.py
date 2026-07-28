"""Dependências FastAPI compartilhadas."""

from __future__ import annotations

from fastapi import HTTPException

from loterias_core.lotteries import LOTTERIES_BY_KEY, LotteryConfig


def resolve_lottery(lottery_key: str) -> LotteryConfig:
    """Resolve a modalidade do catálogo ou responde 404."""
    config = LOTTERIES_BY_KEY.get(lottery_key)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"Loteria desconhecida: '{lottery_key}'.",
            headers={"X-Error-Code": "NOT_FOUND"},
        )
    return config
