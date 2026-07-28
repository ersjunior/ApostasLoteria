"""Valor esperado (EV) e vantagem da casa por modalidade."""

from __future__ import annotations

from dataclasses import dataclass

from loterias_core.combinatorics import win_probability
from loterias_core.lotteries import LotteryConfig

# Prêmios médios aproximados (R$) quando disponíveis — faixa principal.
# Fonte: ordens de grandeza publicadas pela Caixa; variam por concurso.
_AVERAGE_MAIN_PRIZES: dict[str, float] = {
    "megasena": 40_000_000.0,
    "lotofacil": 1_500_000.0,
    "quina": 3_000_000.0,
    "duplasena": 5_000_000.0,
    "diadesorte": 500_000.0,
}


@dataclass(frozen=True)
class PrizeTier:
    """Faixa de premiação com probabilidade e prêmio médio opcional."""

    name: str
    matches: int
    probability: float
    avg_prize: float | None


@dataclass(frozen=True)
class ExpectedValueResult:
    """Resultado do cálculo de valor esperado."""

    cost: float
    main_tier: PrizeTier
    expected_return: float | None
    expected_value: float | None
    house_edge_pct: float | None
    has_prize_data: bool
    note: str


def _main_tier_name(config: LotteryConfig) -> tuple[str, int]:
    """Nome e número de acertos da faixa principal."""
    names: dict[str, tuple[str, int]] = {
        "megasena": ("Sena (6 acertos)", 6),
        "lotofacil": ("15 acertos", 15),
        "quina": ("Quina (5 acertos)", 5),
        "duplasena": ("Sena em qualquer sorteio", 6),
        "lotomania": ("20 acertos", 20),
        "diadesorte": ("7 acertos", 7),
        "timemania": ("7 acertos + time", 7),
        "supersete": ("7 acertos", 7),
        "mais_milionaria": ("6 acertos + 2 trevos", 6),
    }
    return names.get(config.key, ("Faixa principal", config.total_bolas))


def calculate_expected_value(
    config: LotteryConfig,
    qtd_dezenas: int,
    qtd_apostas: int = 1,
) -> ExpectedValueResult:
    """
    Calcula valor esperado da aposta.

    EV = P(prêmio) × prêmio_médio − custo.
    Quando não há dado de prêmio, retorna ``expected_return=None`` e
    destaca probabilidade e custo.
    """
    prob_result = win_probability(config, qtd_dezenas, qtd_apostas)
    tier_name, matches = _main_tier_name(config)

    cost_per_bet = config.price_table[qtd_dezenas]
    total_cost = cost_per_bet * qtd_apostas

    avg_prize = _AVERAGE_MAIN_PRIZES.get(config.key)
    main_tier = PrizeTier(
        name=tier_name,
        matches=matches,
        probability=prob_result.probability,
        avg_prize=avg_prize,
    )

    if avg_prize is not None:
        expected_return = prob_result.probability * avg_prize
        expected_value = expected_return - total_cost
        house_edge = (1 - expected_return / total_cost) * 100 if total_cost > 0 else None
        note = (
            f"Prêmio médio estimado de R$ {avg_prize:,.2f} para referência. "
            "O valor real varia a cada concurso."
        )
        return ExpectedValueResult(
            cost=total_cost,
            main_tier=main_tier,
            expected_return=expected_return,
            expected_value=expected_value,
            house_edge_pct=house_edge,
            has_prize_data=True,
            note=note,
        )

    note = (
        "Dado de prêmio médio indisponível para esta modalidade. "
        "Exibimos probabilidade da faixa principal e custo da aposta."
    )
    return ExpectedValueResult(
        cost=total_cost,
        main_tier=main_tier,
        expected_return=None,
        expected_value=None,
        house_edge_pct=None,
        has_prize_data=False,
        note=note,
    )
