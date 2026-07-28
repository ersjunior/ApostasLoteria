"""Catálogo de loterias suportadas pela API."""

from __future__ import annotations

from fastapi import APIRouter

from api.services.core import list_lotteries

router = APIRouter(tags=["lotteries"])


@router.get("/lotteries")
def get_lotteries():
    """Lista modalidades do catálogo com status de cache no SQLite."""
    items = list_lotteries()
    return {"count": len(items), "lotteries": items}
