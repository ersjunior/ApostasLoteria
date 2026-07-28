import pandas as pd
import pytest

from loterias_core.combinatorics import (
    LOTOMANIA_DEZENAS_APOSTA,
    combination,
    total_combinations,
    win_probability,
)
from loterias_core.lotteries import LOTTERIES_BY_KEY
from loterias_core.statistics import chi_square_uniformity_test, frequency

# --- C(n,k) por modalidade ---


@pytest.mark.parametrize(
    ("key", "n", "k", "expected"),
    [
        ("megasena", 60, 6, 50_063_860),
        ("lotofacil", 25, 15, 3_268_760),
        ("quina", 80, 5, 24_040_016),
        ("duplasena", 50, 6, 15_890_700),
        ("diadesorte", 31, 7, 2_629_575),
        ("timemania", 80, 7, 3_176_716_400),
    ],
)
def test_combination_values(key, n, k, expected):
    assert combination(n, k) == expected
    cfg = LOTTERIES_BY_KEY[key]
    if key not in ("timemania",):
        assert total_combinations(cfg) == expected


def test_mais_milionaria_total_combinations():
    cfg = LOTTERIES_BY_KEY["mais_milionaria"]
    assert total_combinations(cfg) == combination(50, 6) * combination(6, 2)
    assert total_combinations(cfg) == 238_360_500


def test_supersete_total_combinations():
    cfg = LOTTERIES_BY_KEY["supersete"]
    assert total_combinations(cfg) == 10**7


def test_lotomania_total_combinations():
    cfg = LOTTERIES_BY_KEY["lotomania"]
    assert total_combinations(cfg) == combination(100, 20)


# --- Probabilidade da faixa principal ---


def test_megasena_main_probability():
    cfg = LOTTERIES_BY_KEY["megasena"]
    result = win_probability(cfg, qtd_dezenas=6)
    assert result.probability == pytest.approx(1 / 50_063_860)


def test_lotofacil_main_probability():
    cfg = LOTTERIES_BY_KEY["lotofacil"]
    result = win_probability(cfg, qtd_dezenas=15)
    assert result.probability == pytest.approx(1 / 3_268_760)


def test_quina_main_probability():
    cfg = LOTTERIES_BY_KEY["quina"]
    result = win_probability(cfg, qtd_dezenas=5)
    assert result.probability == pytest.approx(1 / 24_040_016)


def test_duplasena_two_draws_probability():
    cfg = LOTTERIES_BY_KEY["duplasena"]
    p_one = 1 / 15_890_700
    result = win_probability(cfg, qtd_dezenas=6)
    assert result.probability == pytest.approx(1 - (1 - p_one) ** 2)


def test_mais_milionaria_main_probability():
    cfg = LOTTERIES_BY_KEY["mais_milionaria"]
    result = win_probability(cfg, qtd_dezenas=6)
    assert result.probability == pytest.approx(1 / 238_360_500)


def test_supersete_main_probability():
    cfg = LOTTERIES_BY_KEY["supersete"]
    result = win_probability(cfg, qtd_dezenas=7)
    assert result.probability == pytest.approx(1 / 10_000_000)


def test_lotomania_main_probability():
    cfg = LOTTERIES_BY_KEY["lotomania"]
    result = win_probability(cfg, qtd_dezenas=LOTOMANIA_DEZENAS_APOSTA)
    expected = combination(50, 20) / combination(100, 20)
    assert result.probability == pytest.approx(expected)


# --- Qui-quadrado em dados sintéticos ---


def _uniform_freq(universo: int, draws: int, balls_per_draw: int) -> pd.Series:
    """Frequências perfeitamente uniformes."""
    per_dezena = (draws * balls_per_draw) // universo
    return pd.Series({i: per_dezena for i in range(1, universo + 1)})


def _biased_freq(universo: int) -> pd.Series:
    """Frequências fortemente enviesadas."""
    data = {i: 10 for i in range(1, universo + 1)}
    data[1] = 10_000
    return pd.Series(data)


def test_chi_square_uniform_data_not_rejected():
    freq = _uniform_freq(universo=60, draws=1000, balls_per_draw=6)
    result = chi_square_uniformity_test(freq, universo=60)
    assert result.p_value >= 0.05
    assert "Compatível com aleatoriedade" in result.interpretation


def test_chi_square_biased_data_rejected():
    freq = _biased_freq(universo=60)
    result = chi_square_uniformity_test(freq, universo=60)
    assert result.p_value < 0.05
    assert "significativo" in result.interpretation.lower()


def test_chi_square_from_frequency_helper():
    """Integração com frequency() em dataset sintético uniforme."""
    rows = []
    for _draw in range(200):
        for bola in range(1, 7):
            rows.append(
                {
                    "bola1": bola,
                    "bola2": bola + 1,
                    "bola3": bola + 2,
                    "bola4": bola + 3,
                    "bola5": bola + 4,
                    "bola6": bola + 5,
                }
            )
    df = pd.DataFrame(rows)
    freq = frequency(df, total_bolas=6)
    # Dataset pequeno e repetitivo — apenas verifica que roda sem erro
    result = chi_square_uniformity_test(freq, universo=60)
    assert result.degrees_of_freedom == 59
    assert result.statistic >= 0
