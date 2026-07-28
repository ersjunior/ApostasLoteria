from __future__ import annotations

from dataclasses import dataclass
from math import exp, lgamma, log

import pandas as pd

# Constantes numéricas da gama incompleta (Numerical Recipes)
_GAMMAINCC_TINY = 1e-300
_GAMMAINCC_EPS = 1e-14
_GAMMAINCC_MAX_ITER = 500


@dataclass(frozen=True)
class ChiSquareResult:
    """Resultado do teste qui-quadrado de aderência à uniformidade."""

    statistic: float
    p_value: float
    degrees_of_freedom: int
    interpretation: str
    n_observations: int


def _gammaincc(a: float, x: float) -> float:
    """
    Função gama incompleta superior regularizada Q(a, x) = 1 − P(a, x).

    Implementação sem SciPy (Numerical Recipes): série de potências para
    ``x < a + 1`` e fração continuada de Lentz para ``x ≥ a + 1``.

    O fator de normalização é ``exp(-x + a·ln(x) − lnΓ(a))`` — numericamente
    estável e limitado (≈ densidade gama no ponto). A versão anterior usava
    ``exp(-x + a·lnΓ(a))``, cujo termo `a·lnΓ(a)` cresce sem limite e causava
    ``OverflowError: math range error`` para graus de liberdade típicos
    (ex.: Mega-Sena, df = 59 → a = 29.5).
    """
    if x <= 0.0 or a <= 0.0:
        return 1.0

    gln = lgamma(a)
    # Fator comum ~ x^a · e^-x / Γ(a): limitado, não estoura.
    prefactor = exp(-x + a * log(x) - gln)

    if x < a + 1.0:
        # Série → P(a, x) (cauda inferior); Q = 1 − P.
        ap = a
        summ = 1.0 / a
        term = summ
        for _ in range(_GAMMAINCC_MAX_ITER):
            ap += 1.0
            term *= x / ap
            summ += term
            if abs(term) < abs(summ) * _GAMMAINCC_EPS:
                break
        p_lower = summ * prefactor
        return min(max(1.0 - p_lower, 0.0), 1.0)

    # Fração continuada de Lentz → Q(a, x) (cauda superior) diretamente.
    b = x + 1.0 - a
    c = 1.0 / _GAMMAINCC_TINY
    d = 1.0 / b
    h = d
    for i in range(1, _GAMMAINCC_MAX_ITER):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < _GAMMAINCC_TINY:
            d = _GAMMAINCC_TINY
        c = b + an / c
        if abs(c) < _GAMMAINCC_TINY:
            c = _GAMMAINCC_TINY
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _GAMMAINCC_EPS:
            break
    q_upper = h * prefactor
    return min(max(q_upper, 0.0), 1.0)


def _chi2_sf(x: float, df: int) -> float:
    """Probabilidade da cauda superior (survival) da distribuição qui-quadrado."""
    if x <= 0 or df <= 0:
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


def _coerce_dezenas(value) -> list[int]:
    """Normaliza um valor de ``jogo`` (lista, tupla ou string) para lista de ints."""
    if value is None:
        return []

    if isinstance(value, (list, tuple)):
        try:
            return [int(v) for v in value]
        except (TypeError, ValueError):
            return []

    if isinstance(value, str):
        cleaned = value.strip().replace("[", "").replace("]", "")
        parts = [p.strip() for p in cleaned.split(",") if p.strip()]
        try:
            return [int(p) for p in parts]
        except ValueError:
            return []

    return []


def _collect_numbers(df: pd.DataFrame, total_bolas: int) -> list:
    """
    Extrai dezenas do DataFrame.

    Prefere a coluna canônica ``jogo`` (loaders especiais / Dupla Sena).
    Fallback para ``bola1..bolaN`` (datasets crus / testes legados).
    """
    if "jogo" in df.columns:
        nums: list = []
        for value in df["jogo"]:
            nums.extend(_coerce_dezenas(value))
        return nums

    nums = []
    for i in range(1, total_bolas + 1):
        col = f"bola{i}"
        if col in df.columns:
            nums.extend(df[col].tolist())
    return nums


def frequency(df, total_bolas: int):
    """
    Calcula a frequência das dezenas para qualquer loteria.
    """
    nums = _collect_numbers(df, total_bolas)
    if not nums:
        return pd.Series(dtype=int)
    return pd.Series(nums).value_counts().sort_index()


def empirical_probability(df, total_bolas: int):
    """
    Calcula a probabilidade empírica das dezenas.
    """
    freq = frequency(df, total_bolas)
    total = int(freq.sum())
    if total == 0:
        return freq
    return freq / total


def frequency_by_period(df, last_n: int = 50, total_bolas: int = 6):
    """Frequência das dezenas nos últimos ``last_n`` sorteios."""
    return frequency(df.tail(last_n), total_bolas)


def _resolve_column(df: pd.DataFrame, field: str) -> str | None:
    """Localiza coluna por nome exato ou normalizado (minúsculas, sem espaços)."""
    if field in df.columns:
        return field

    def _norm(name: str) -> str:
        return str(name).lower().replace(" ", "").replace("_", "")

    target = _norm(field)
    for col in df.columns:
        if _norm(col) == target:
            return str(col)
    return None


def extra_field_frequency(df: pd.DataFrame, field: str) -> pd.Series:
    """
    Frequência de um campo extra (trevos, time do coração, etc.).

    Aceita valores escalares ou listas por linha.
    """
    col = _resolve_column(df, field)
    if col is None:
        return pd.Series(dtype=int)

    values: list = []
    for raw in df[col]:
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            continue
        if isinstance(raw, (list, tuple)):
            values.extend(raw)
        else:
            values.append(raw)

    if not values:
        return pd.Series(dtype=int)

    # Times / labels como string; números como int quando possível
    normalized = []
    for v in values:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            try:
                normalized.append(int(v))
                continue
            except (TypeError, ValueError):
                pass
        text = str(v).strip()
        if text.isdigit():
            normalized.append(int(text))
        elif text:
            normalized.append(text)

    if not normalized:
        return pd.Series(dtype=int)
    return pd.Series(normalized).value_counts()


def frequency_by_draw(df: pd.DataFrame, total_bolas: int) -> dict[int, pd.Series]:
    """Frequência clássica agrupada por ``draw_index`` (Dupla Sena)."""
    if "draw_index" not in df.columns:
        return {}

    result: dict[int, pd.Series] = {}
    for draw_id, group in df.groupby("draw_index"):
        result[int(draw_id)] = frequency(group, total_bolas)
    return result


def frequency_by_position(df: pd.DataFrame, n_positions: int) -> pd.DataFrame:
    """
    Frequência por posição no ``jogo`` (Super Sete: coluna 1..N).

    Retorna DataFrame com colunas ``coluna``, ``digito``, ``frequencia``.
    """
    if "jogo" not in df.columns or n_positions <= 0:
        return pd.DataFrame(columns=["coluna", "digito", "frequencia"])

    records: list[dict] = []
    for pos in range(n_positions):
        vals: list[int] = []
        for jogo in df["jogo"]:
            nums = _coerce_dezenas(jogo)
            if pos < len(nums):
                vals.append(nums[pos])
        if not vals:
            continue
        counts = pd.Series(vals).value_counts()
        for digito, count in counts.items():
            records.append(
                {
                    "coluna": pos + 1,
                    "digito": int(digito),
                    "frequencia": int(count),
                }
            )

    if not records:
        return pd.DataFrame(columns=["coluna", "digito", "frequencia"])
    return pd.DataFrame(records)
