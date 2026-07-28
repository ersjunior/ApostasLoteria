"""Testes de geração de relatório PDF."""

from io import BytesIO
from unittest.mock import patch

import pandas as pd
import pytest

from app.services.report import generate_statistics_pdf

# PNG 1×1 válido para o ReportLab aceitar como imagem
_MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _run_pdf(df, total_bolas: int = 6, titulo: str = "Relatório Estatístico"):
    freq = pd.Series({i: 1 for i in range(1, 61)})
    prob = freq / freq.sum()

    with patch("app.services.report.frequency", return_value=freq) as mock_freq:
        with patch("app.services.report.empirical_probability", return_value=prob) as mock_prob:
            with patch(
                "app.services.report._plotly_to_image",
                return_value=BytesIO(_MINIMAL_PNG),
            ):
                buffer = generate_statistics_pdf(df, total_bolas=total_bolas, titulo=titulo)

    return buffer, mock_freq, mock_prob


def test_generate_statistics_pdf_returns_non_empty_buffer(sample_megasena_df):
    buffer, mock_freq, mock_prob = _run_pdf(sample_megasena_df, total_bolas=6)

    assert isinstance(buffer, BytesIO)
    content = buffer.getvalue()
    assert len(content) > 100
    assert content[:4] == b"%PDF"

    mock_freq.assert_called_once_with(sample_megasena_df, total_bolas=6)
    mock_prob.assert_called_once_with(sample_megasena_df, total_bolas=6)


def test_generate_statistics_pdf_custom_titulo(sample_megasena_df):
    buffer, _, _ = _run_pdf(
        sample_megasena_df,
        total_bolas=6,
        titulo="Relatório Estatístico — Lotofácil",
    )
    assert buffer.getvalue()[:4] == b"%PDF"


def test_generate_statistics_pdf_empty_freq_raises(sample_megasena_df):
    empty = pd.Series(dtype=int)

    with patch("app.services.report.frequency", return_value=empty):
        with patch("app.services.report.empirical_probability", return_value=empty):
            with pytest.raises(ValueError, match="Nenhum dado estatístico"):
                generate_statistics_pdf(sample_megasena_df, total_bolas=6)


def test_generate_statistics_pdf_without_chart_when_plotly_fails(sample_megasena_df):
    """PDF segue válido só com tabelas se Kaleido/Chrome falhar."""
    freq = pd.Series({i: 1 for i in range(1, 61)})
    prob = freq / freq.sum()

    with patch("app.services.report.frequency", return_value=freq):
        with patch("app.services.report.empirical_probability", return_value=prob):
            with patch(
                "app.services.report._plotly_to_image",
                side_effect=RuntimeError("Chrome/Kaleido indisponível"),
            ):
                buffer = generate_statistics_pdf(
                    sample_megasena_df,
                    total_bolas=6,
                    titulo="Relatório sem gráfico",
                )

    content = buffer.getvalue()
    assert isinstance(buffer, BytesIO)
    assert len(content) > 100
    assert content[:4] == b"%PDF"
