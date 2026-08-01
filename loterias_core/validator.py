"""Verificação de jogos contra o histórico oficial."""

from __future__ import annotations

from typing import Any

# Faixas de acertos relevantes (estilo Lotofácil: 11 a 15).
HIT_TIERS: tuple[int, ...] = (11, 12, 13, 14, 15)


def _normalize_game(value: Any) -> list[int] | None:
    """Normaliza um jogo (lista, tupla ou string) para lista ordenada de inteiros."""
    if value is None:
        return None

    if isinstance(value, (list, tuple)):
        try:
            return sorted(int(v) for v in value)
        except (TypeError, ValueError):
            return None

    if isinstance(value, str):
        value = value.strip().replace("[", "").replace("]", "")
        parts = [p.strip() for p in value.split(",") if p.strip().lstrip("-").isdigit()]
        try:
            return sorted(int(p) for p in parts)
        except (TypeError, ValueError):
            return None

    return None


def check_game(dezenas: list[int], df, extra_values: dict | None = None) -> bool:
    """
    Verifica se um jogo já foi sorteado.
    Suporta:
    - dezenas principais
    - campos extras (ex: trevos)
    - datasets heterogêneos da Caixa
    """

    # 🔒 Blindagem absoluta
    if df is None or df.empty or "jogo" not in df.columns:
        return False

    # 🔢 Normalização das dezenas de entrada
    try:
        dezenas = sorted(int(v) for v in dezenas)
    except (TypeError, ValueError):
        return False

    # =========================
    # CASO COM CAMPOS EXTRAS
    # =========================
    if extra_values:
        # Normalizar extras de entrada
        normalized_extras = {}
        for field, values in extra_values.items():
            try:
                normalized_extras[field] = sorted(int(v) for v in values)
            except (TypeError, ValueError):
                return False

        for _, row in df.iterrows():
            jogo_row = _normalize_game(row.get("jogo"))

            if jogo_row != dezenas:
                continue

            extras_ok = True
            for field, expected in normalized_extras.items():
                row_extra = _normalize_game(row.get(field))
                if row_extra != expected:
                    extras_ok = False
                    break

            if extras_ok:
                return True

        return False

    # =========================
    # CASO SEM CAMPOS EXTRAS
    # =========================
    return any(_normalize_game(jogo) == dezenas for jogo in df["jogo"])


def count_hit_tiers(
    dezenas: list[int],
    df,
    *,
    tiers: tuple[int, ...] = HIT_TIERS,
) -> dict[int, int]:
    """
    Conta quantos sorteios históricos batem exatamente N dezenas com a aposta.

    Para cada concurso, calcula o tamanho da interseção entre as dezenas da
    aposta e as dezenas sorteadas. Incrementa o contador da faixa correspondente
    quando o número de acertos está em ``tiers`` (padrão: 11–15).

    Modalidades com menos de 11 dezenas no sorteio terão todos os contadores
    em zero — o que é esperado (ex.: Mega-Sena, Quina).
    """
    counts = {tier: 0 for tier in tiers}
    if df is None or getattr(df, "empty", True) or "jogo" not in getattr(df, "columns", []):
        return counts

    try:
        bet = {int(v) for v in dezenas}
    except (TypeError, ValueError):
        return counts

    if not bet:
        return counts

    tier_set = set(tiers)
    for jogo in df["jogo"]:
        jogo_norm = _normalize_game(jogo)
        if jogo_norm is None:
            continue
        hits = len(bet.intersection(jogo_norm))
        if hits in tier_set:
            counts[hits] += 1

    return counts


def analyze_game(
    dezenas: list[int],
    df,
    *,
    extra_values: dict | None = None,
    tiers: tuple[int, ...] = HIT_TIERS,
) -> dict[str, Any]:
    """
    Análise completa: match exato + volumes por faixa de acertos.

    Retorna:
        exact_match: bool
        tier_counts: dict[int, int]  (chaves 11..15 por padrão)
        hits_above_11: bool  (True se houve algum acerto em 12, 13, 14 ou 15)
    """
    exact = check_game(dezenas, df, extra_values=extra_values)
    tier_counts = count_hit_tiers(dezenas, df, tiers=tiers)
    hits_above_11 = any(tier_counts.get(t, 0) > 0 for t in (12, 13, 14, 15))
    return {
        "exact_match": exact,
        "tier_counts": tier_counts,
        "hits_above_11": hits_above_11,
    }
