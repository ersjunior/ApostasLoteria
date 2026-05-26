from io import BytesIO
import tempfile

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

import plotly.express as px
import plotly.graph_objects as go

from app.services.statistics import frequency, empirical_probability



def _plotly_to_image(fig, width=800, height=400):
    """
    Converte um gráfico Plotly para imagem PNG (BytesIO)
    """
    img_bytes = fig.to_image(
        format="png",
        width=width,
        height=height,
        scale=2
    )
    return BytesIO(img_bytes)


def generate_statistics_pdf(df, total_bolas: int, titulo: str = "Relatório Estatístico"):
    freq = frequency(df, total_bolas=total_bolas)
    prob = empirical_probability(df, total_bolas=total_bolas)
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # =========================
    # TÍTULO
    # =========================
    elements.append(Paragraph(
        "<b>Mega-Sena Analyzer</b>", styles["Title"]
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        "Relatório Estatístico Completo - Histórico da Mega-Sena",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 20))

    # =========================
    # KPIs
    # =========================
    freq = frequency(df)
    prob = empirical_probability(df)

    kpi_data = [
        ["Indicador", "Valor"],
        ["Total de Concursos", str(len(df))],
        ["Dezena Mais Sorteada", str(freq.idxmax())],
        ["Dezena Menos Sorteada", str(freq.idxmin())],
        ["Diferença Máx / Mín", str(freq.max() - freq.min())],
    ]

    table = Table(kpi_data, colWidths=[220, 180])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(Paragraph("Resumo Geral", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(table)
    elements.append(Spacer(1, 25))

    # =========================
    # GRÁFICO DE FREQUÊNCIA (BAR)
    # =========================
    freq_df = freq.reset_index()
    freq_df.columns = ["Dezena", "Frequência"]

    fig_bar = px.bar(
        freq_df,
        x="Dezena",
        y="Frequência",
        title="Frequência Histórica das Dezenas",
        color="Frequência",
        color_continuous_scale="Blues"
    )
    fig_bar.update_layout(coloraxis_showscale=False)

    elements.append(Paragraph("Frequência das Dezenas", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(Image(_plotly_to_image(fig_bar), width=500, height=280))
    elements.append(Spacer(1, 25))

    # =========================
    # RANKING
    # =========================
    ranking = freq.sort_values(ascending=False).head(10)

    ranking_data = [["Dezena", "Quantidade"]] + [
        [str(idx), str(val)] for idx, val in ranking.items()
    ]

    ranking_table = Table(ranking_data, colWidths=[220, 180])
    ranking_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(Paragraph("Top 10 Dezenas Mais Sorteadas", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    elements.append(ranking_table)
    elements.append(Spacer(1, 25))

    # =========================
    # OBSERVAÇÕES
    # =========================
    elements.append(Paragraph("Observações Importantes", styles["Heading3"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(
        """
        A Mega-Sena é um jogo de natureza totalmente aleatória.
        Todas as análises apresentadas neste relatório são baseadas
        exclusivamente em dados históricos e não representam
        qualquer garantia de resultados futuros.
        """,
        styles["Normal"]
    ))

    # =========================
    # BUILD
    # =========================
    doc.build(elements)
    buffer.seek(0)
    return buffer
