"""Modelos Pydantic para validação de entrada da API."""

from __future__ import annotations

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from api.config import get_settings


class GameRequest(BaseModel):
    """Corpo do POST /verify/."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    numbers: list[int] = Field(
        ...,
        min_length=6,
        max_length=6,
        description="Seis dezenas da Mega-Sena",
    )

    @field_validator("numbers")
    @classmethod
    def validate_megasena_numbers(cls, numbers: list[int]) -> list[int]:
        if len(set(numbers)) != 6:
            raise ValueError("Os números devem ser distintos")
        if not all(1 <= number <= 60 for number in numbers):
            raise ValueError("Os números devem estar entre 1 e 60")
        return numbers


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
