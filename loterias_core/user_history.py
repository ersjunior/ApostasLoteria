"""Histórico local de jogos do usuário (SQLite — sem autenticação)."""

from __future__ import annotations

from typing import Any

from loterias_core.storage import (
    add_user_game,
    clear_user_games,
    delete_user_game,
    list_user_games,
)

SOURCE_VERIFY = "verify"
SOURCE_COMBINATIONS = "combinations"
SOURCE_MANUAL = "manual"

__all__ = [
    "SOURCE_COMBINATIONS",
    "SOURCE_MANUAL",
    "SOURCE_VERIFY",
    "add_user_game",
    "add_user_games",
    "clear_user_games",
    "delete_user_game",
    "list_user_games",
]


def add_user_games(
    lottery_key: str,
    games: list[dict[str, Any]],
    *,
    source: str = SOURCE_MANUAL,
    note: str | None = None,
) -> list[int]:
    """
    Persiste vários jogos.

    Cada item deve ter ``dezenas`` (list[int]) e opcionalmente ``extras`` (dict).
    """
    ids: list[int] = []
    for game in games:
        dezenas = list(game["dezenas"])
        extras = game.get("extras") or None
        ids.append(
            add_user_game(
                lottery_key,
                dezenas,
                extras=extras if extras else None,
                source=source,
                note=note,
            )
        )
    return ids
