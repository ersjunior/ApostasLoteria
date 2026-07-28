from __future__ import annotations

from dataclasses import dataclass
from math import exp, lgamma

import pandas as pd


@dataclass(frozen=True)
class ChiSquareResult:
    """Resultado do teste qui-quadrado de aderência à uniformidade."""

    statistic: float
    p_value: float
    degrees_of_freedom: int
    interpretation: str
    n_observations: int


def _gammaincc(a: float, x: float) -> float:
    """Função gama incompleta superior normalizada Q(a, x)."""
    if x < 0 or a <= 0:
        return 1.0
    if x < a + 1:
        # Série de convergência
        ap = a
        summ = 1.0 / a
        del_ = summ
        for _n in range(1, 200):
            ap += 1.0
            del_ *= x / ap
            summ += del_
            if abs(del_) < abs(summ) * 1e-10:
                break
        return summ * exp(-x + a * lgamma(a))
    # Fração continuada de Lentz
    b = x + 1.0 - a
    c = 1.0 / 1e-30
    d = 1.0 / b
    h = d
    for i in range(1, 200):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        del_ = d * c
        h *= del_
        if abs(del_ - 1.0) < 1e-10:
            break
    return h * exp(-x + a * lgamma(a))


def _chi2_sf(x: float, df: int) -> float:
    """Probabilidade da cauda superior da distribuição qui-quadrado."""
    if x <= 0:
        return 1.0
    return _gammaincc(df / 2.0, x / 2.0)


def chi_square_uniformity_test(
    freq: pd.Series,
    universo: int,
    alpha: float = 0.05,
) -> ChiSquareResult:
    """
    Teste qui-quadrado de aderência: frequências observadas vs. uniforme.

    H₀: cada dezena tem a mesma probabilidade de ser sorteada.
    """
    observed = []
    for dezena in range(1, universo + 1):
        observed.append(int(freq.get(dezena, 0)))

    n_total = sum(observed)
    expected = n_total / universo

    if expected == 0:
        return ChiSquareResult(
            statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=max(universo - 1, 0),
            interpretation="Dados insuficientes para o teste.",
            n_observations=0,
        )

    chi2 = sum((o - expected) ** 2 / expected for o in observed)
    df = universo - 1
    p_value = _chi2_sf(chi2, df)

    if p_value >= alpha:
        interpretation = "Compatível com aleatoriedade (não rejeita H₀ ao nível de 5%)."
    else:
        interpretation = (
            "Desvio estatisticamente significativo em relação à uniformidade "
            f"(p < {alpha:.0%}). Isso não implica padrão previsível — pode ser ruído amostral "
            "ou mudança de procedimento ao longo do tempo."
        )

    return ChiSquareResult(
        statistic=chi2,
        p_value=p_value,
        degrees_of_freedom=df,
        interpretation=interpretation,
        n_observations=n_total,
    )


def frequency(df, total_bolas: int):
    """
    Calcula a frequência das dezenas para qualquer loteria
    """
    nums = []

    for i in range(1, total_bolas + 1):
        col = f"bola{i}"
        if col in df.columns:
            nums.extend(df[col].tolist())

    return pd.Series(nums).value_counts().sort_index()


def empirical_probability(df, total_bolas: int):
    """
    Calcula a probabilidade empírica das dezenas
    """
    freq = frequency(df, total_bolas)
    total_sorteios = len(df) * total_bolas
    return freq / total_sorteios


def frequency_by_period(df, last_n=50):
    df_slice = df.tail(last_n)

    nums = []
    for i in range(1, 7):
        nums.extend(df_slice[f"bola{i}"].tolist())

    return pd.Series(nums).value_counts().sort_index()
