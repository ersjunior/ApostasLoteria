"""Camada fina Streamlit sobre o histórico local de jogos."""

from __future__ import annotations

from typing import Any

import pandas as pd

from loterias_core.user_history import (
    SOURCE_COMBINATIONS,
    SOURCE_MANUAL,
    SOURCE_VERIFY,
    add_user_game,
    add_user_games,
    clear_user_games,
    delete_user_game,
    list_user_games,
)

__all__ = [
    "SOURCE_COMBINATIONS",
    "SOURCE_MANUAL",
    "SOURCE_VERIFY",
    "add_user_game",
    "add_user_games",
    "clear_user_games",
    "delete_user_game",
    "export_history_csv",
    "list_user_games",
]


def export_history_csv(rows: list[dict[str, Any]]) -> bytes:
    """Exporta linhas do histórico para CSV UTF-8."""
    if not rows:
        raise ValueError("Nenhum jogo no histórico para exportar.")

    records = []
    for row in rows:
        extras = row.get("extras") or {}
        extras_str = "; ".join(
            f"{field}={','.join(str(v) for v in values)}" for field, values in extras.items()
        )
        records.append(
            {
                "id": row["id"],
                "lottery_key": row["lottery_key"],
                "dezenas": ",".join(str(n) for n in row["dezenas"]),
                "extras": extras_str,
                "source": row["source"],
                "note": row.get("note") or "",
                "created_at": row["created_at"],
            }
        )

    return pd.DataFrame(records).to_csv(index=False).encode("utf-8")
