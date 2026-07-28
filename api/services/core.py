"""Serviços core da API — delegam ao pacote loterias_core."""

import os

import pandas as pd

from loterias_core.generator import generate_unique_combinations
from loterias_core.scraper import download_megasena_data
from loterias_core.validator import check_game

DATASET_PATH = "app/data/megasena.csv"


def load_dataset():
    """Carrega o dataset da Mega-Sena (CSV legado da API)."""
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset não encontrado em {DATASET_PATH}. Por favor, atualize o dataset primeiro."
        )
    return pd.read_csv(DATASET_PATH)


def update_dataset():
    """Atualiza o dataset baixando a versão mais recente."""
    df = download_megasena_data()
    df.columns = [c.lower() for c in df.columns]

    dezenas = ["bola_1", "bola_2", "bola_3", "bola_4", "bola_5", "bola_6"]

    df["jogo"] = df[dezenas].apply(lambda x: sorted(x.values.tolist()), axis=1)

    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
    return df


def verify_game(numbers: list[int]) -> bool:
    """Verifica se um jogo já foi sorteado."""
    df = load_dataset()
    return check_game(sorted(numbers), df)


def generate_unique_combination_games(n: int = 10):
    """Gera combinações inéditas com base no histórico da Mega-Sena."""
    df = load_dataset()
    return generate_unique_combinations(df, n_games=n, total_bolas=6, universo=60)
