import pandas as pd

from loterias_core.validator import analyze_game, check_game, count_hit_tiers


def test_game():
    df = pd.DataFrame({"jogo": ["[1,2,3,4,5,6]"]})
    assert check_game([1, 2, 3, 4, 5, 6], df) is True


def test_count_hit_tiers_lotofacil_style():
    # Aposta com 15 dezenas; sorteios com interseções 15, 14, 12 e 10.
    bet = list(range(1, 16))
    draws = [
        list(range(1, 16)),  # 15 acertos
        list(range(1, 15)) + [20],  # 14 acertos
        list(range(1, 13)) + [20, 21, 22],  # 12 acertos
        list(range(1, 11)) + [20, 21, 22, 23, 24],  # 10 acertos (fora das faixas)
        list(range(1, 16)),  # 15 acertos de novo
    ]
    df = pd.DataFrame({"jogo": draws})

    counts = count_hit_tiers(bet, df)
    assert counts[15] == 2
    assert counts[14] == 1
    assert counts[13] == 0
    assert counts[12] == 1
    assert counts[11] == 0


def test_analyze_game_flags_hits_above_11():
    bet = list(range(1, 16))
    df = pd.DataFrame({"jogo": [list(range(1, 13)) + [20, 21, 22]]})  # 12 acertos
    result = analyze_game(bet, df)
    assert result["exact_match"] is False
    assert result["hits_above_11"] is True
    assert result["tier_counts"][12] == 1


def test_count_hit_tiers_empty_for_small_lotteries():
    # Mega-Sena: no máximo 6 acertos — faixas 11–15 ficam zeradas.
    df = pd.DataFrame({"jogo": [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 7]]})
    counts = count_hit_tiers([1, 2, 3, 4, 5, 6], df)
    assert all(v == 0 for v in counts.values())
    assert check_game([1, 2, 3, 4, 5, 6], df) is True


def test_count_hit_tiers_never_exceeds_draw_count():
    """Soma das faixas de um jogo ≤ número de sorteios da base."""
    bet = list(range(1, 16))
    draws = [list(range(1, 16)) for _ in range(50)] + [
        list(range(1, 12)) + [20, 21, 22, 23] for _ in range(30)
    ]
    df = pd.DataFrame({"jogo": draws})
    counts = count_hit_tiers(bet, df)
    assert sum(counts.values()) <= len(draws)
    assert counts[15] == 50
    assert counts[11] == 30
