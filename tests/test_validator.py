import pandas as pd

from app.services.validator import check_game


def test_game():
    df = pd.DataFrame({"jogo": ["[1,2,3,4,5,6]"]})
    assert check_game([1, 2, 3, 4, 5, 6], df) is True
