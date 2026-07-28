"""Configuração da API via variáveis de ambiente."""

from __future__ import annotations

import os
from functools import lru_cache


def _parse_origins(raw: str | None) -> list[str]:
    if not raw or not raw.strip():
        return []
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


class Settings:
    """Configurações carregadas uma vez por processo."""

    def __init__(self) -> None:
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.environment: str = os.getenv("ENVIRONMENT", "development").lower()
        self.cors_origins: list[str] = _parse_origins(os.getenv("CORS_ORIGINS"))
        self.max_body_bytes: int = int(os.getenv("MAX_BODY_BYTES", "10240"))
        self.max_forecast_n: int = int(os.getenv("MAX_FORECAST_N", "100"))
        self.rate_limit_dataset: str = os.getenv("RATE_LIMIT_DATASET", "3/hour")
        self.rate_limit_forecast: str = os.getenv("RATE_LIMIT_FORECAST", "30/minute")
        self.rate_limit_combinations: str = os.getenv("RATE_LIMIT_COMBINATIONS", "60/minute")

    @property
    def effective_cors_origins(self) -> list[str]:
        """Em produção sem CORS_ORIGINS explícito, não permite nenhuma origem."""
        if self.cors_origins:
            return self.cors_origins
        if self.environment == "production":
            return []
        return ["http://localhost:8501", "http://127.0.0.1:8501"]
