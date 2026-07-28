"""Rota de health check."""

from __future__ import annotations

from fastapi import APIRouter

from api.services.core import health_info

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """
    Verifica se a API está operacional e reporta status do banco SQLite
    e cache por modalidade.
    """
    payload = health_info()
    return {"status": "ok", **payload}
