"""Fonte única de domínio para loterias brasileiras (sem Streamlit nem FastAPI)."""

from loterias_core.dataset import (
    enrich_dataset,
    handle_lotomania,
    handle_mais_milionaria,
    handle_supersete,
    load_dataset,
    normalize_columns,
    save_dataset,
)
from loterias_core.generator import generate_forecast_games
from loterias_core.lotteries import LOTTERIES, LOTTERY_CONFIGS, LotteryConfig
from loterias_core.scraper import download_megasena_data
from loterias_core.statistics import empirical_probability, frequency, frequency_by_period
from loterias_core.validator import check_game

__all__ = [
    "LOTTERIES",
    "LOTTERY_CONFIGS",
    "LotteryConfig",
    "check_game",
    "download_megasena_data",
    "empirical_probability",
    "enrich_dataset",
    "frequency",
    "frequency_by_period",
    "generate_forecast_games",
    "handle_lotomania",
    "handle_mais_milionaria",
    "handle_supersete",
    "load_dataset",
    "normalize_columns",
    "save_dataset",
]
