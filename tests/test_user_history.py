"""Testes do histórico local de jogos do usuário."""

from __future__ import annotations

from loterias_core.storage import init_db
from loterias_core.user_history import (
    SOURCE_COMBINATIONS,
    SOURCE_VERIFY,
    add_user_game,
    add_user_games,
    clear_user_games,
    delete_user_game,
    list_user_games,
)
from app.services.user_history import export_history_csv


def test_add_list_delete_user_game(db_path):
    init_db(str(db_path))
    game_id = add_user_game(
        "megasena",
        [1, 2, 3, 4, 5, 6],
        source=SOURCE_VERIFY,
        note="teste",
    )
    assert game_id > 0

    rows = list_user_games("megasena")
    assert len(rows) == 1
    assert rows[0]["dezenas"] == [1, 2, 3, 4, 5, 6]
    assert rows[0]["source"] == SOURCE_VERIFY
    assert rows[0]["note"] == "teste"

    assert delete_user_game(game_id) is True
    assert list_user_games("megasena") == []
    assert delete_user_game(game_id) is False


def test_add_user_games_batch_and_clear(db_path):
    init_db(str(db_path))
    ids = add_user_games(
        "quina",
        [
            {"dezenas": [1, 2, 3, 4, 5]},
            {"dezenas": [6, 7, 8, 9, 10], "extras": None},
        ],
        source=SOURCE_COMBINATIONS,
    )
    assert len(ids) == 2
    assert len(list_user_games("quina")) == 2

    add_user_game("megasena", [10, 20, 30, 40, 50, 60], source=SOURCE_VERIFY)
    assert len(list_user_games()) == 3

    removed = clear_user_games("quina")
    assert removed == 2
    assert len(list_user_games("quina")) == 0
    assert len(list_user_games()) == 1

    assert clear_user_games() == 1
    assert list_user_games() == []


def test_list_user_games_with_extras(db_path):
    init_db(str(db_path))
    add_user_game(
        "maismilionaria",
        [1, 2, 3, 4, 5, 6],
        extras={"trevos": [1, 2]},
        source=SOURCE_COMBINATIONS,
    )
    rows = list_user_games("maismilionaria")
    assert rows[0]["extras"]["trevos"] == [1, 2]


def test_export_history_csv(db_path):
    init_db(str(db_path))
    add_user_game("megasena", [1, 2, 3, 4, 5, 6], source=SOURCE_VERIFY)
    rows = list_user_games()
    raw = export_history_csv(rows)
    text = raw.decode("utf-8")
    assert "lottery_key" in text
    assert "1,2,3,4,5,6" in text
