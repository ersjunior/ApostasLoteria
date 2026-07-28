import pandas as pd

from loterias_core.statistics import (
    empirical_probability,
    extra_field_frequency,
    frequency,
    frequency_by_draw,
    frequency_by_period,
    frequency_by_position,
)


def mock_dataset():
    data = {
        "bola1": [1, 1],
        "bola2": [2, 2],
        "bola3": [3, 3],
        "bola4": [4, 4],
        "bola5": [5, 5],
        "bola6": [6, 6],
    }
    return pd.DataFrame(data)


def test_frequency_counts_correctly():
    df = mock_dataset()
    freq = frequency(df, total_bolas=6)

    assert freq[1] == 2
    assert freq[6] == 2
    assert freq.sum() == 12  # 2 concursos * 6 dezenas


def test_empirical_probability():
    df = mock_dataset()
    prob = empirical_probability(df, total_bolas=6)

    assert prob.min() >= 0
    assert round(prob.sum(), 5) == 1.0


def test_frequency_from_jogo_column():
    df = pd.DataFrame(
        {
            "jogo": [
                [1, 2, 3, 4, 5, 6],
                [1, 10, 20, 30, 40, 50],
            ]
        }
    )
    freq = frequency(df, total_bolas=6)

    assert freq[1] == 2
    assert freq[6] == 1
    assert freq[10] == 1
    assert freq.sum() == 12


def test_frequency_includes_zero_from_jogo():
    """Super Sete / Lotomania podem sortear o dígito 0."""
    df = pd.DataFrame({"jogo": [[0, 1, 2, 3, 4, 5, 6], [0, 7, 8, 9, 1, 2, 3]]})
    freq = frequency(df, total_bolas=7)

    assert freq[0] == 2
    assert freq.sum() == 14


def test_frequency_ignores_trevos_column():
    """+Milionária: conta só dezenas em jogo, não trevos."""
    df = pd.DataFrame(
        {
            "jogo": [[1, 2, 3, 4, 5, 6]],
            "trevos": [[1, 2]],
        }
    )
    freq = frequency(df, total_bolas=6)

    assert list(freq.index) == [1, 2, 3, 4, 5, 6]
    assert freq.sum() == 6


def test_empirical_probability_from_jogo():
    df = pd.DataFrame({"jogo": [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]})
    prob = empirical_probability(df, total_bolas=6)

    assert round(prob.sum(), 5) == 1.0


def test_frequency_by_period_uses_last_n_from_jogo():
    df = pd.DataFrame(
        {
            "jogo": [
                [1, 2, 3, 4, 5, 6],
                [7, 8, 9, 10, 11, 12],
                [13, 14, 15, 16, 17, 18],
            ]
        }
    )
    freq = frequency_by_period(df, last_n=1, total_bolas=6)

    assert list(freq.index) == [13, 14, 15, 16, 17, 18]
    assert freq.sum() == 6


def test_extra_field_frequency_trevos():
    df = pd.DataFrame(
        {
            "jogo": [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]],
            "trevos": [[1, 2], [1, 3]],
        }
    )
    freq = extra_field_frequency(df, "trevos")

    assert freq[1] == 2
    assert freq[2] == 1
    assert freq[3] == 1
    assert freq.sum() == 4


def test_extra_field_frequency_timecoracao():
    df = pd.DataFrame(
        {
            "jogo": [[1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14]],
            "timecoração": ["Flamengo", "Palmeiras"],
        }
    )
    freq = extra_field_frequency(df, "timecoração")

    assert freq["Flamengo"] == 1
    assert freq["Palmeiras"] == 1


def test_extra_field_frequency_resolves_normalized_column():
    df = pd.DataFrame({"Time Coracao": ["ABC", "ABC", "XYZ"]})
    freq = extra_field_frequency(df, "timecoracao")

    assert freq["ABC"] == 2
    assert freq["XYZ"] == 1


def test_frequency_by_draw_dupla_sena():
    df = pd.DataFrame(
        {
            "draw_index": [1, 1, 2, 2],
            "jogo": [
                [1, 2, 3, 4, 5, 6],
                [1, 2, 3, 4, 5, 7],
                [10, 11, 12, 13, 14, 15],
                [10, 11, 12, 13, 14, 16],
            ],
        }
    )
    by_draw = frequency_by_draw(df, total_bolas=6)

    assert set(by_draw) == {1, 2}
    assert by_draw[1][1] == 2
    assert by_draw[1][6] == 1
    assert by_draw[1][7] == 1
    assert by_draw[2][10] == 2
    assert 1 not in by_draw[2].index


def test_frequency_by_draw_without_column_returns_empty():
    df = pd.DataFrame({"jogo": [[1, 2, 3, 4, 5, 6]]})
    assert frequency_by_draw(df, total_bolas=6) == {}


def test_frequency_by_position_supersete():
    df = pd.DataFrame(
        {
            "jogo": [
                [0, 1, 2, 3, 4, 5, 6],
                [0, 1, 7, 8, 9, 0, 1],
            ]
        }
    )
    pos = frequency_by_position(df, n_positions=7)

    assert list(pos.columns) == ["coluna", "digito", "frequencia"]
    col1 = pos[pos["coluna"] == 1]
    assert int(col1[col1["digito"] == 0]["frequencia"].iloc[0]) == 2
    col2 = pos[pos["coluna"] == 2]
    assert int(col2[col2["digito"] == 1]["frequencia"].iloc[0]) == 2
    col3 = pos[pos["coluna"] == 3]
    assert set(col3["digito"]) == {2, 7}
