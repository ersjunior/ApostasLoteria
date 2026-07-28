"""Gera datasets sintéticos pequenos por modalidade (sem rede)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd

FIXTURES_DIR = Path(__file__).resolve().parent


def _write_xlsx(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False, engine="openpyxl")
    return path


def megasena_xlsx(path: Path | None = None) -> Path:
    df = pd.DataFrame(
        {
            "Concurso": [1, 2],
            "Bola1": [1, 10],
            "Bola2": [2, 20],
            "Bola3": [3, 30],
            "Bola4": [4, 40],
            "Bola5": [5, 50],
            "Bola6": [6, 60],
        }
    )
    return _write_xlsx(df, path or FIXTURES_DIR / "megasena.xlsx")


def lotofacil_xlsx(path: Path | None = None) -> Path:
    row1 = list(range(1, 16))
    row2 = list(range(2, 17))
    df = pd.DataFrame(
        {
            "Concurso": [1, 2],
            **{f"Bola{i}": [row1[i - 1], row2[i - 1]] for i in range(1, 16)},
        }
    )
    return _write_xlsx(df, path or FIXTURES_DIR / "lotofacil.xlsx")


def quina_xlsx(path: Path | None = None) -> Path:
    df = pd.DataFrame(
        {
            "Concurso": [1, 2],
            "Bola1": [1, 10],
            "Bola2": [2, 20],
            "Bola3": [3, 30],
            "Bola4": [4, 40],
            "Bola5": [5, 50],
        }
    )
    return _write_xlsx(df, path or FIXTURES_DIR / "quina.xlsx")


def duplasena_xlsx(path: Path | None = None) -> Path:
    cols: dict[str, list[int]] = {"Concurso": [1, 2]}
    for draw in (1, 2):
        for i in range(1, 7):
            cols[f"Bola{i}Sorteio{draw}"] = [i + draw - 1, i + 10 + draw - 1]
    return _write_xlsx(pd.DataFrame(cols), path or FIXTURES_DIR / "duplasena.xlsx")


def lotomania_xlsx(path: Path | None = None) -> Path:
    cols: dict[str, list[int]] = {"Concurso": [1, 2]}
    for i in range(1, 51):
        cols[f"Bola{i}"] = [i, i + 50]
    return _write_xlsx(pd.DataFrame(cols), path or FIXTURES_DIR / "lotomania.xlsx")


def diadesorte_xlsx(path: Path | None = None) -> Path:
    df = pd.DataFrame(
        {
            "Concurso": [1, 2],
            **{f"Bola{i}": [i, i + 7] for i in range(1, 8)},
        }
    )
    return _write_xlsx(df, path or FIXTURES_DIR / "diadesorte.xlsx")


def timemania_xlsx(path: Path | None = None) -> Path:
    df = pd.DataFrame(
        {
            "Concurso": [1, 2],
            **{f"Bola{i}": [i, i + 7] for i in range(1, 8)},
            "Timecoração": ["Flamengo", "Corinthians"],
        }
    )
    return _write_xlsx(df, path or FIXTURES_DIR / "timemania.xlsx")


def supersete_xlsx(path: Path | None = None) -> Path:
    df = pd.DataFrame(
        {
            "Concurso": [1, 2],
            **{f"Coluna{i}": [i % 10, (i + 1) % 10] for i in range(1, 8)},
        }
    )
    return _write_xlsx(df, path or FIXTURES_DIR / "supersete.xlsx")


def mais_milionaria_xlsx(path: Path | None = None) -> Path:
    df = pd.DataFrame(
        {
            "Concurso": [1, 2],
            **{f"Bola{i}": [i, i + 6] for i in range(1, 7)},
            "Trevo1": [1, 3],
            "Trevo2": [2, 4],
        }
    )
    return _write_xlsx(df, path or FIXTURES_DIR / "mais_milionaria.xlsx")


def megasena_csv(path: Path | None = None) -> Path:
    target = path or FIXTURES_DIR / "megasena.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        {
            "concurso": [1, 2],
            "bola1": [1, 10],
            "bola2": [2, 20],
            "bola3": [3, 30],
            "bola4": [4, 40],
            "bola5": [5, 50],
            "bola6": [6, 60],
            "jogo": [[1, 2, 3, 4, 5, 6], [10, 20, 30, 40, 50, 60]],
        }
    )
    df.to_csv(target, index=False)
    return target


def megasena_xlsx_bytes() -> bytes:
    buf = BytesIO()
    pd.read_excel(megasena_xlsx()).to_excel(buf, index=False)
    return buf.getvalue()


def build_all_fixtures() -> dict[str, Path]:
    """Materializa todos os arquivos de fixture em disco."""
    return {
        "megasena": megasena_xlsx(),
        "lotofacil": lotofacil_xlsx(),
        "quina": quina_xlsx(),
        "duplasena": duplasena_xlsx(),
        "lotomania": lotomania_xlsx(),
        "diadesorte": diadesorte_xlsx(),
        "timemania": timemania_xlsx(),
        "supersete": supersete_xlsx(),
        "mais_milionaria": mais_milionaria_xlsx(),
        "megasena_csv": megasena_csv(),
    }
