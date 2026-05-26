import pandas as pd
from app.ml.forecast import train_model, predict_games

def mock_dataset():
    data = {
        "bola1": [1, 2, 3, 4, 5, 6, 7],
        "bola2": [10, 11, 12, 13, 14, 15, 16],
        "bola3": [20, 21, 22, 23, 24, 25, 26],
        "bola4": [30, 31, 32, 33, 34, 35, 36],
        "bola5": [40, 41, 42, 43, 44, 45, 46],
        "bola6": [50, 51, 52, 53, 54, 55, 56],
    }
    return pd.DataFrame(data)

def test_train_returns_6_models():
    df = mock_dataset()
    models = train_model(df)

    assert isinstance(models, dict)
    assert len(models) == 6

def test_predict_returns_valid_games():
    df = mock_dataset()
    models = train_model(df)

    games = predict_games(models, start=len(df), n=5)

    assert isinstance(games, list)
    assert len(games) == 5

    for game in games:
        assert len(game) == 6
        assert all(isinstance(n, int) for n in game)
        assert all(1 <= n <= 60 for n in game)
