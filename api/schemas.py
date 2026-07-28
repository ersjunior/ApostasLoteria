"""Modelos Pydantic para validação de entrada da API."""

from __future__ import annotations

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from api.config import get_settings
from loterias_core.lotteries import LotteryConfig


class GameRequest(BaseModel):
    """Corpo do POST .../verify — validação fina depende do LotteryConfig."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    numbers: list[int] = Field(
        ...,
        min_length=1,
        description="Dezenas principais do jogo",
    )
    extras: dict[str, list[int]] | None = Field(
        default=None,
        description="Campos extras opcionais (ex.: trevos, timecoração)",
    )


def _number_range(config: LotteryConfig) -> tuple[int, int]:
    """Retorna (mínimo, máximo) inclusivos das dezenas principais."""
    if config.special_handler in ("supersete", "lotomania"):
        return 0, config.universo - 1
    return 1, config.universo


def validate_game_against_config(
    numbers: list[int],
    extras: dict[str, list[int]] | None,
    config: LotteryConfig,
) -> tuple[list[int], dict[str, list[int]] | None]:
    """
    Valida dezenas (e extras) contra a modalidade.

    Raises:
        ValueError: mensagem legível para resposta 422.
    """
    expected = config.total_bolas
    if len(numbers) != expected:
        raise ValueError(f"Informe exatamente {expected} dezenas para {config.name}.")

    if len(set(numbers)) != len(numbers):
        raise ValueError("Os números devem ser distintos.")

    lo, hi = _number_range(config)
    if not all(lo <= n <= hi for n in numbers):
        raise ValueError(f"Os números devem estar entre {lo} e {hi}.")

    normalized_extras: dict[str, list[int]] | None = None
    extra_fields = config.extra_fields or {}

    if extras:
        normalized_extras = {}
        for field, values in extras.items():
            if not isinstance(values, list) or not values:
                raise ValueError(f"Campo extra '{field}' deve ser uma lista não vazia.")
            if len(set(values)) != len(values):
                raise ValueError(f"Valores de '{field}' devem ser distintos.")
            if field in extra_fields and len(values) != extra_fields[field]:
                raise ValueError(
                    f"Campo '{field}' exige exatamente {extra_fields[field]} valor(es)."
                )
            normalized_extras[field] = sorted(int(v) for v in values)

    return sorted(numbers), normalized_extras


class NGamesQuery(BaseModel):
    """Query param compartilhado por /forecast/ e /combinations/."""

    model_config = ConfigDict(extra="forbid")

    n: int = Field(
        default=10,
        ge=1,
        description="Quantidade de combinações inéditas a gerar",
    )

    @field_validator("n")
    @classmethod
    def validate_n_limit(cls, value: int) -> int:
        max_n = get_settings().max_forecast_n
        if value > max_n:
            raise ValueError(f"O parâmetro n não pode ser maior que {max_n}")
        return value


def n_games_query(
    n: int = Query(
        default=10,
        ge=1,
        le=get_settings().max_forecast_n,
        description="Quantidade de combinações inéditas a gerar",
    ),
) -> NGamesQuery:
    try:
        return NGamesQuery(n=n)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc
