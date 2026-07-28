"""Testes da camada de cache Streamlit."""

from unittest.mock import MagicMock, patch

import pandas as pd


def test_load_dataset_cached_delegates_to_loader():
    expected = pd.DataFrame({"jogo": [[1, 2, 3, 4, 5, 6]]})
    with patch("app.services.cache.load_dataset", return_value=expected) as mock_load:
        from app.services.cache import load_dataset_cached

        result = load_dataset_cached()
        mock_load.assert_called_once_with()
        pd.testing.assert_frame_equal(result, expected)


def test_app_dataset_load_internal_bypasses_cache(megasena_fixture):
    with patch("app.services.dataset.st") as mock_st:
        mock_st.cache_data = lambda **kwargs: lambda fn: fn
        from app.services.dataset import load_dataset_internal

        df = load_dataset_internal(str(megasena_fixture), total_bolas=6)
        assert len(df) == 2
        assert "jogo" in df.columns


def test_app_save_dataset_clears_cache(megasena_fixture, tmp_path):
    with patch("app.services.dataset.st") as mock_st:
        mock_st.cache_data.clear = MagicMock()
        from app.services.dataset import save_dataset

        raw = pd.read_excel(megasena_fixture)
        out = tmp_path / "cached_save.xlsx"
        save_dataset(raw, str(out), total_bolas=6)
        mock_st.cache_data.clear.assert_called_once()
        assert out.exists()
