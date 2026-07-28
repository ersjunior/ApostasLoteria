import pandas as pd

from app.ml.forecast import generate_forecast_games


def mock_dataset():
    return pd.DataFrame(
        {
            "jogo": [
                [1, 10, 20, 30, 40, 50],
                [2, 11, 21, 31, 41, 51],
            ]
        }
    )


def test_generate_returns_valid_games():
    df = mock_dataset()
    games = generate_forecast_games(df, n_games=5, total_bolas=6, universo=60)

    assert isinstance(games, list)
    assert len(games) == 5

    existing = {tuple(sorted(j)) for j in df["jogo"]}
    for game in games:
        dezenas = game["dezenas"]
        assert len(dezenas) == 6
        assert all(isinstance(n, int) for n in dezenas)
        assert all(1 <= n <= 60 for n in dezenas)
        assert dezenas == sorted(dezenas)
        assert tuple(dezenas) not in existing
