"""Testes de exportação CSV."""

import pytest

from app.services.exporter import export_csv


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
