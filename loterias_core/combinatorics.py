"""Combinatória e probabilidades por modalidade de loteria."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb

from loterias_core.lotteries import LotteryConfig

# Constantes de referência para trevos (+Milionária) e times (Timemania)
TREVOS_UNIVERSO = 6
TREVOS_POR_APOSTA = 2
TIMES_UNIVERSO = 80
SUPER_SETE_COLUNAS = 7
SUPER_SETE_DIGITOS = 10
LOTOMANIA_DEZENAS_APOSTA = 50
LOTOMANIA_DEZENAS_SORTEIO = 20


@dataclass(frozen=True)
class ProbabilityResult:
    """Resultado de probabilidade para uma aposta."""

    total_combinations: int
    bet_combinations: int
    probability: float
    formula: str


def combination(n: int, k: int) -> int:
    """C(n, k) com validação de parâmetros."""
    if k < 0 or n < 0 or k > n:
        return 0
    return comb(n, k)


def total_combinations(config: LotteryConfig) -> int:
    """Total de combinações possíveis na modalidade (faixa principal)."""
    key = config.key

    if key == "supersete":
        return SUPER_SETE_DIGITOS**SUPER_SETE_COLUNAS

    if key == "mais_milionaria":
        return combination(config.universo, config.total_bolas) * combination(
            TREVOS_UNIVERSO, TREVOS_POR_APOSTA
        )

    if key == "timemania":
        return combination(config.universo, config.total_bolas) * TIMES_UNIVERSO

    if key == "lotomania":
        return combination(config.universo, LOTOMANIA_DEZENAS_SORTEIO)

    return combination(config.universo, config.total_bolas)


def bet_combinations(config: LotteryConfig, qtd_dezenas: int) -> int:
    """Combinações cobertas por uma aposta com ``qtd_dezenas`` números."""
    key = config.key

    if key == "supersete":
        return 1

    if key == "mais_milionaria":
        return combination(qtd_dezenas, config.total_bolas)

    if key == "timemania":
        return combination(qtd_dezenas, config.total_bolas)

    if key == "lotomania":
        return combination(qtd_dezenas, LOTOMANIA_DEZENAS_SORTEIO)

    return combination(qtd_dezenas, config.total_bolas)


def win_probability(
    config: LotteryConfig,
    qtd_dezenas: int,
    qtd_apostas: int = 1,
) -> ProbabilityResult:
    """
    Probabilidade de acertar a faixa principal (prêmio máximo).

    Dupla Sena: dois sorteios independentes — P = 1 − (1 − p)².
    """
    total = total_combinations(config)
    covered = bet_combinations(config, qtd_dezenas)
    key = config.key

    if key == "duplasena":
        p_draw = covered / total
        prob = 1 - (1 - p_draw) ** 2
        formula = (
            f"1 − (1 − C({qtd_dezenas},{config.total_bolas})/"
            f"C({config.universo},{config.total_bolas}))²"
        )
    elif key == "supersete":
        prob = covered / total
        formula = f"1 / {SUPER_SETE_DIGITOS}^{SUPER_SETE_COLUNAS}"
    elif key == "mais_milionaria":
        prob = covered / total
        formula = (
            f"C({qtd_dezenas},{config.total_bolas}) / "
            f"(C({config.universo},{config.total_bolas}) × "
            f"C({TREVOS_UNIVERSO},{TREVOS_POR_APOSTA}))"
        )
    elif key == "timemania":
        prob = covered / total
        formula = (
            f"C({qtd_dezenas},{config.total_bolas}) / "
            f"(C({config.universo},{config.total_bolas}) × {TIMES_UNIVERSO})"
        )
    elif key == "lotomania":
        prob = covered / total
        formula = (
            f"C({qtd_dezenas},{LOTOMANIA_DEZENAS_SORTEIO}) / "
            f"C({config.universo},{LOTOMANIA_DEZENAS_SORTEIO})"
        )
    else:
        prob = covered / total
        formula = f"C({qtd_dezenas},{config.total_bolas}) / C({config.universo},{config.total_bolas})"

    if qtd_apostas > 1:
        prob = 1 - (1 - prob) ** qtd_apostas

    return ProbabilityResult(
        total_combinations=total,
        bet_combinations=covered,
        probability=prob,
        formula=formula,
    )


def get_lottery_config_from_dict(config_dict: dict) -> LotteryConfig:
    """Reconstrói ``LotteryConfig`` a partir do dict usado na UI."""
    from loterias_core.lotteries import LOTTERIES_BY_KEY

    key = config_dict["key"]
    if key in LOTTERIES_BY_KEY:
        return LOTTERIES_BY_KEY[key]

    return LotteryConfig(
        name=config_dict.get("name", key),
        key=key,
        icon=config_dict.get("icon", ""),
        color=config_dict.get("color", ""),
        total_bolas=config_dict["total_bolas"],
        universo=config_dict["universo"],
        placeholder=config_dict.get("placeholder", ""),
        file_path=config_dict["file_path"],
        price_table=config_dict["price_table"],
        multiple_draws=config_dict.get("multiple_draws", False),
        special_handler=config_dict.get("special_handler"),
        extra_fields=config_dict.get("extra_fields"),
    )
