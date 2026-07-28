import pandas as pd

from loterias_core.statistics import empirical_probability, frequency


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
