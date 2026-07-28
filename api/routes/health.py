"""Rota de health check."""

from __future__ import annotations

from fastapi import APIRouter

from api.services.core import get_dataset_status

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """
    Verifica se a API está operacional e reporta status do dataset Mega-Sena.
    """
    dataset = get_dataset_status()
    return {
        "status": "ok",
        "dataset": dataset,
    }
