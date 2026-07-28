"""Testes do cálculo de valor esperado (EV) e da validação de preço por dezenas."""

import pytest

from loterias_core.expected_value import calculate_expected_value
from loterias_core.lotteries import LOTTERIES_BY_KEY, LOTTERY_CONFIGS


@pytest.mark.parametrize("cfg", LOTTERY_CONFIGS, ids=lambda c: c.key)
def test_ev_valid_for_every_price_table_key(cfg):
    """Toda quantidade de dezenas com preço definido deve calcular EV sem erro."""
    for qtd_dezenas in sorted(cfg.price_table):
        result = calculate_expected_value(cfg, qtd_dezenas, qtd_apostas=1)
        assert result.cost == pytest.approx(cfg.price_table[qtd_dezenas])
        assert 0.0 <= result.main_tier.probability <= 1.0


def test_ev_raises_value_error_for_dezenas_without_price():
    """Regressão: dezenas acima do desdobramento não devem gerar KeyError cru.

    Antes, selecionar > 20 dezenas na Mega-Sena estourava com ``KeyError: 21``.
    """
    mega = LOTTERIES_BY_KEY["megasena"]
    with pytest.raises(ValueError, match="sem preço definido"):
        calculate_expected_value(mega, 21, qtd_apostas=1)


def test_ev_cost_scales_with_number_of_bets():
    """Custo total = custo unitário × número de apostas."""
    mega = LOTTERIES_BY_KEY["megasena"]
    result = calculate_expected_value(mega, 6, qtd_apostas=5)
    assert result.cost == pytest.approx(mega.price_table[6] * 5)
