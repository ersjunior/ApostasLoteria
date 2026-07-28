"""Geração de relatório estatístico em PDF."""

from __future__ import annotations

import logging
from io import BytesIO

import plotly.express as px
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.statistics import empirical_probability, frequency

logger = logging.getLogger(__name__)

_TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]
)


def _plotly_to_image(fig, width=800, height=400):
    """Converte um gráfico Plotly para imagem PNG (BytesIO)."""
    img_bytes = fig.to_image(format="png", width=width, height=height, scale=2)
    return BytesIO(img_bytes)


def _make_table(data: list[list[str]], col_widths: list[int] | None = None) -> Table:
    table = Table(data, colWidths=col_widths or [220, 180])
    table.setStyle(_TABLE_STYLE)
    return table


def generate_statistics_pdf(df, total_bolas: int, titulo: str = "Relatório Estatístico"):
    """
    Gera um PDF com KPIs, frequência, ranking e probabilidade empírica.

    Se a exportação do gráfico Plotly falhar (ex.: Kaleido/Chrome ausente),
    o PDF segue só com tabelas e um aviso no lugar do gráfico.

    Returns:
        BytesIO posicionado no início, contendo o PDF.
    """
    freq = frequency(df, total_bolas=total_bolas)
    prob = empirical_probability(df, total_bolas=total_bolas)

    if freq.empty:
        raise ValueError("Nenhum dado estatístico para exportar.")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>ApostasLoteria</b>", styles["Title"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(titulo, styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # KPIs
    kpi_data = [
        ["Indicador", "Valor"],
        ["Total de Concursos", str(len(df))],
        ["Dezena Mais Sorteada", str(freq.idxmax())],
        ["Dezena Menos Sorteada", str(freq.idxmin())],
        ["Diferença Máx / Mín", str(int(freq.max() - freq.min()))],
    ]
    elements.append(Paragraph("Resumo Geral", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(_make_table(kpi_data))
    elements.append(Spacer(1, 25))

    # Gráfico de frequência (opcional — Kaleido/Chrome pode faltar em Docker slim)
    freq_df = freq.reset_index()
    freq_df.columns = ["Dezena", "Frequência"]

    fig_bar = px.bar(
        freq_df,
        x="Dezena",
        y="Frequência",
        title="Frequência Histórica das Dezenas",
        color="Frequência",
        color_continuous_scale="Blues",
    )
    fig_bar.update_layout(coloraxis_showscale=False)

    elements.append(Paragraph("Frequência das Dezenas", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    try:
        elements.append(Image(_plotly_to_image(fig_bar), width=500, height=280))
    except Exception:
        logger.warning(
            "Gráfico de frequência omitido no PDF (Kaleido/Chrome indisponível).", exc_info=True
        )
        elements.append(
            Paragraph(
                "Gráfico de frequência indisponível neste ambiente.",
                styles["Normal"],
            )
        )
    elements.append(Spacer(1, 25))

    # Top 10 frequência
    ranking = freq.sort_values(ascending=False).head(10)
    ranking_data = [["Dezena", "Quantidade"]] + [
        [str(idx), str(val)] for idx, val in ranking.items()
    ]
    elements.append(Paragraph("Top 10 Dezenas Mais Sorteadas", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(_make_table(ranking_data))
    elements.append(Spacer(1, 25))

    # Top 10 probabilidade empírica
    top_prob = prob.sort_values(ascending=False).head(10)
    prob_data = [["Dezena", "Probabilidade"]] + [
        [str(idx), f"{val:.4%}"] for idx, val in top_prob.items()
    ]
    elements.append(Paragraph("Top 10 Probabilidade Empírica", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(_make_table(prob_data))
    elements.append(Spacer(1, 25))

    # Observações
    elements.append(Paragraph("Observações Importantes", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(
            "Loterias são jogos de natureza totalmente aleatória. "
            "Todas as análises deste relatório baseiam-se exclusivamente em dados históricos "
            "e não representam qualquer garantia de resultados futuros.",
            styles["Normal"],
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
