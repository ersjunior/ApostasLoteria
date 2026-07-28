import pandas as pd

from loterias_core.generator import generate_unique_combinations


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
    games = generate_unique_combinations(df, n_games=5, total_bolas=6, universo=60)

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
        assert game["extras"] is None


def test_generate_includes_trevos_for_mais_milionaria():
    df = mock_dataset()
    games = generate_unique_combinations(
        df,
        n_games=5,
        total_bolas=6,
        universo=50,
        extra_fields={"trevos": 2, "trevos_universo": 6},
    )

    assert len(games) == 5
    for game in games:
        extras = game["extras"]
        assert extras is not None
        assert "trevos" in extras
        trevos = extras["trevos"]
        assert len(trevos) == 2
        assert trevos == sorted(trevos)
        assert all(1 <= t <= 6 for t in trevos)
        assert len(set(trevos)) == 2


def test_mais_milionaria_catalog_declares_trevos():
    from loterias_core.lotteries import LOTTERIES_BY_KEY

    cfg = LOTTERIES_BY_KEY["mais_milionaria"]
    data = cfg.to_dict()
    assert data["extra_fields"]["trevos"] == 2
    assert data["extra_fields"]["trevos_universo"] == 6
