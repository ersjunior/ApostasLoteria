"""Serialização de jogos para CSV (UTF-8)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd


def export_csv(games: Sequence[Any], prefix: str = "Bola") -> bytes:
    """
    Exporta jogos para CSV de forma genérica
    (funciona para Mega-Sena, Lotofácil, etc.).

    Aceita:
      - lista de listas/tuplas: ``[[1, 2, 3, ...], ...]``
      - lista de dicts do generator: ``[{"dezenas": [...], "extras": {...}|None}, ...]``
    """
    if not games:
        raise ValueError("Nenhum jogo para exportar.")

    flattened = [_flatten_game(game) for game in games]
    columns, rows = _build_table(flattened, prefix=prefix)
    df = pd.DataFrame(rows, columns=columns)
    return df.to_csv(index=False).encode("utf-8")


def _flatten_game(game: Any) -> tuple[list[Any], dict[str, list[Any]]]:
    """Normaliza um jogo para ``(dezenas, extras)``."""
    if isinstance(game, Mapping):
        if "dezenas" not in game:
            raise TypeError("Jogo em dict deve conter a chave 'dezenas'.")
        dezenas = list(game["dezenas"])
        extras_raw = game.get("extras") or {}
        if not isinstance(extras_raw, Mapping):
            raise TypeError("Campo 'extras' deve ser um dict ou None.")
        extras = {str(field): list(values) for field, values in extras_raw.items()}
        return dezenas, extras

    if isinstance(game, (list, tuple)):
        return list(game), {}

    raise TypeError(
        f"Formato de jogo não suportado: {type(game).__name__}. "
        "Use lista de dezenas ou dict com chave 'dezenas'."
    )


def _build_table(
    flattened: list[tuple[list[Any], dict[str, list[Any]]]],
    prefix: str,
) -> tuple[list[str], list[list[Any]]]:
    """Monta colunas e linhas alinhadas a partir dos jogos normalizados."""
    n_dezenas = max(len(dezenas) for dezenas, _ in flattened)
    if n_dezenas == 0:
        raise ValueError("Nenhum jogo para exportar.")

    extra_widths: dict[str, int] = {}
    for _, extras in flattened:
        for field, values in extras.items():
            extra_widths[field] = max(extra_widths.get(field, 0), len(values))

    columns = [f"{prefix}{i}" for i in range(1, n_dezenas + 1)]
    for field, width in extra_widths.items():
        label = field.capitalize()
        columns.extend(f"{label}{i}" for i in range(1, width + 1))

    rows: list[list[Any]] = []
    for dezenas, extras in flattened:
        row: list[Any] = list(dezenas) + [""] * (n_dezenas - len(dezenas))
        for field, width in extra_widths.items():
            values = extras.get(field, [])
            row.extend(list(values) + [""] * (width - len(values)))
        rows.append(row)

    return columns, rows
