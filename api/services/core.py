"""
Serviços core para a API.
NOTA: Este arquivo pode estar obsoleto.
As funcionalidades já estão implementadas em app/services/ e as rotas da API
estão usando diretamente os serviços de app/.

Este arquivo mantém compatibilidade caso seja necessário no futuro.
"""

import os

import pandas as pd

from app.ml.forecast import generate_forecast_games
from app.services.scraper import download_megasena_data
from app.services.validator import check_game

DATASET_PATH = "app/data/megasena.csv"


# =========================
# DATASET
# =========================
def load_dataset():
    """
    Carrega o dataset da Mega-Sena
    """
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset não encontrado em {DATASET_PATH}. Por favor, atualize o dataset primeiro."
        )
    return pd.read_csv(DATASET_PATH)


def update_dataset():
    """
    Atualiza o dataset baixando a versão mais recente
    """
    df = download_megasena_data()
    df.columns = [c.lower() for c in df.columns]

    # Usar o padrão correto de nomes de colunas (bola_1, bola_2, etc.)
    dezenas = ["bola_1", "bola_2", "bola_3", "bola_4", "bola_5", "bola_6"]

    df["jogo"] = df[dezenas].apply(lambda x: sorted(x.values.tolist()), axis=1)

    # Garantir que o diretório existe
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
    return df


# =========================
# VERIFICAÇÃO DE JOGOS
# =========================
def verify_game(numbers: list[int]) -> bool:
    """
    Verifica se um jogo já foi sorteado
    """
    df = load_dataset()
    return check_game(sorted(numbers), df)


# =========================
# FORECAST
# =========================
def forecast_games(n: int = 10):
    """
    Gera jogos inéditos (nunca sorteados) com base no histórico da Mega-Sena.
    """
    df = load_dataset()
    return generate_forecast_games(df, n_games=n, total_bolas=6, universo=60)
