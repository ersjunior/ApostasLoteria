"""Testes de geração de relatório PDF."""

from io import BytesIO
from unittest.mock import patch

import pandas as pd

from app.services.report import generate_statistics_pdf

# PNG 1×1 válido para o ReportLab aceitar como imagem
_MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_generate_statistics_pdf_returns_non_empty_buffer(sample_megasena_df):
    freq = pd.Series({i: 1 for i in range(1, 61)})

    with patch("app.services.report.frequency", return_value=freq):
        with patch("app.services.report.empirical_probability", return_value=freq / freq.sum()):
            with patch(
                "app.services.report._plotly_to_image",
                return_value=BytesIO(_MINIMAL_PNG),
            ):
                buffer = generate_statistics_pdf(sample_megasena_df, total_bolas=6)

    assert isinstance(buffer, BytesIO)
    content = buffer.getvalue()
    assert len(content) > 100
    assert content[:4] == b"%PDF"
