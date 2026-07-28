"""Fonte única de domínio para loterias brasileiras (sem Streamlit nem FastAPI)."""

from loterias_core.combinatorics import (
    combination,
    get_lottery_config_from_dict,
    total_combinations,
    win_probability,
)
from loterias_core.dataset import (
    enrich_dataset,
    handle_lotomania,
    handle_mais_milionaria,
    handle_supersete,
    load_dataset,
    normalize_columns,
    save_dataset,
)
from loterias_core.expected_value import calculate_expected_value
from loterias_core.generator import generate_unique_combinations
from loterias_core.lotteries import LOTTERIES, LOTTERY_CONFIGS, LotteryConfig
from loterias_core.scraper import download_megasena_data
from loterias_core.statistics import (
    ChiSquareResult,
    chi_square_uniformity_test,
    empirical_probability,
    frequency,
    frequency_by_period,
)
from loterias_core.validator import check_game

__all__ = [
    "LOTTERIES",
    "LOTTERY_CONFIGS",
    "ChiSquareResult",
    "LotteryConfig",
    "calculate_expected_value",
    "check_game",
    "chi_square_uniformity_test",
    "combination",
    "download_megasena_data",
    "empirical_probability",
    "enrich_dataset",
    "frequency",
    "frequency_by_period",
    "generate_unique_combinations",
    "get_lottery_config_from_dict",
    "handle_lotomania",
    "handle_mais_milionaria",
    "handle_supersete",
    "load_dataset",
    "normalize_columns",
    "save_dataset",
    "total_combinations",
    "win_probability",
]
