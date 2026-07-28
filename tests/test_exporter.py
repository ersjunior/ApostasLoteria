"""Testes de exportação CSV."""

import pytest

from app.services.exporter import export_csv


def _csv_text(games, **kwargs) -> str:
    return export_csv(games, **kwargs).decode("utf-8").replace(" ", "")


def test_export_csv_returns_utf8_bytes():
    games = [[1, 2, 3, 4, 5, 6], [10, 20, 30, 40, 50, 60]]
    result = export_csv(games)
    assert isinstance(result, bytes)
    text = result.decode("utf-8")
    assert "Bola1" in text
    assert "1,2,3,4,5,6" in text.replace(" ", "")
    assert "10,20,30,40,50,60" in text.replace(" ", "")


def test_export_csv_custom_prefix():
    games = [[1, 2, 3]]
    result = export_csv(games, prefix="Dezena").decode("utf-8")
    assert "Dezena1" in result
    assert "1,2,3" in result.replace(" ", "")


def test_export_csv_empty_raises():
    with pytest.raises(ValueError, match="Nenhum jogo"):
        export_csv([])


def test_export_csv_structured_games_without_extras():
    games = [
        {"dezenas": [1, 2, 3, 4, 5, 6], "extras": None},
        {"dezenas": [10, 20, 30, 40, 50, 60], "extras": None},
    ]
    text = _csv_text(games)
    assert "Bola1,Bola2,Bola3,Bola4,Bola5,Bola6" in text
    assert "1,2,3,4,5,6" in text
    assert "10,20,30,40,50,60" in text
    assert "Trevos" not in text


def test_export_csv_structured_games_with_extras():
    games = [{"dezenas": [1, 2, 3, 4, 5, 6], "extras": {"trevos": [1, 3]}}]
    text = _csv_text(games)
    assert "Bola1,Bola2,Bola3,Bola4,Bola5,Bola6,Trevos1,Trevos2" in text
    assert "1,2,3,4,5,6,1,3" in text


def test_export_csv_mixed_extras_aligns_columns():
    games = [
        {"dezenas": [1, 2, 3, 4, 5, 6], "extras": {"trevos": [1, 3]}},
        {"dezenas": [7, 8, 9, 10, 11, 12], "extras": None},
    ]
    text = _csv_text(games)
    header, row1, row2, *_ = text.strip().splitlines()
    assert header == "Bola1,Bola2,Bola3,Bola4,Bola5,Bola6,Trevos1,Trevos2"
    assert row1 == "1,2,3,4,5,6,1,3"
    assert row2 == "7,8,9,10,11,12,,"


def test_export_csv_dict_without_dezenas_raises():
    with pytest.raises(TypeError, match="dezenas"):
        export_csv([{}])
