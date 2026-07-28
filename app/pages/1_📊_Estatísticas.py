import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.services.dataset import load_dataset
from app.services.report import generate_statistics_pdf
from app.services.statistics import (
    chi_square_uniformity_test,
    empirical_probability,
    extra_field_frequency,
    frequency,
    frequency_by_draw,
    frequency_by_position,
)
from app.ui.shell import render_app_chrome, render_lottery_picker
from app.ui.theme import lottery_badge, metric_card, page_title, responsible_gaming_footer, section
from loterias_core.combinatorics import get_lottery_config_from_dict, win_probability
from loterias_core.expected_value import calculate_expected_value

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Estatísticas das Loterias", layout="wide")

render_app_chrome()


def _format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


page_title("📊 Estatísticas das Loterias", "Análise histórica e estatística dos sorteios")
lottery_name, config = render_lottery_picker()
lottery_cfg = get_lottery_config_from_dict(config)
lottery_badge(lottery_name, config)


# =========================
# CARREGAMENTO DO DATASET
# =========================
try:
    df = load_dataset(
        lottery_key=config["key"],
        total_bolas=config["total_bolas"],
        extra_fields=config.get("extra_fields"),
        multiple_draws=config.get("multiple_draws", False),
        special_handler=config.get("special_handler"),
    )
except (FileNotFoundError, ValueError) as e:
    st.error(f"⚠️ Erro ao carregar a base da **{lottery_name}**\n\n{str(e)}")
    st.stop()


# =========================
# VALIDAÇÃO DE ESTRUTURA ESTATÍSTICA
# =========================
if "jogo" not in df.columns or df["jogo"].dropna().empty:
    st.warning(
        "⚠️ Não há coluna `jogo` utilizável nesta base.\n\n"
        "Faça upload novamente do XLSX oficial da modalidade selecionada."
    )
    st.stop()


# =========================
# CÁLCULOS BASE
# =========================
freq = frequency(df, total_bolas=config["total_bolas"])
prob = empirical_probability(df, total_bolas=config["total_bolas"])

freq_df = freq.reset_index()
freq_df.columns = ["Dezena", "Frequência"]

prob_df = prob.reset_index()
prob_df.columns = ["Dezena", "Probabilidade"]


# =========================
# VISÃO GERAL (KPIs)
# =========================
section("📌 Visão Geral")

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

total_concursos = len(df)

if freq.empty:
    dezena_mais = "—"
    dezena_menos = "—"
    dif_max_min = "—"
else:
    dezena_mais = str(freq.idxmax())
    dezena_menos = str(freq.idxmin())
    dif_max_min = int(freq.max() - freq.min())

with col1:
    metric_card("Total de Concursos", f"{total_concursos}", config["icon"])

with col2:
    metric_card("Dezena Mais Sorteada", dezena_mais, "⭐")

with col3:
    metric_card("Dezena Menos Sorteada", dezena_menos, "❄️")

with col4:
    metric_card("Diferença Máx/Mín", str(dif_max_min), "📏")


# =========================
# TESTE QUI-QUADRADO DE UNIFORMIDADE
# =========================
if not freq.empty:
    section("🔬 Teste Qui-Quadrado de Uniformidade")

    chi2 = chi_square_uniformity_test(freq, universo=config["universo"])

    st.markdown(
        """
        Este teste compara a **frequência observada** de cada dezena com a frequência
        **esperada sob sorteio uniforme** (todas as dezenas igualmente prováveis).

        Dezenas "quentes" ou "frias" são, estatisticamente, **ruído amostral** — variações
        naturais que **não aumentam** a chance real no próximo sorteio (falácia do apostador).
        """
    )

    # p-valor sempre com 2 casas decimais; abaixo de 0,01 mostra "< 0.01"
    # para não exibir "0.00" em resultados estatisticamente significativos.
    p_display = f"{chi2.p_value:.2f}" if chi2.p_value >= 0.01 else "< 0.01"

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Estatística χ²", f"{chi2.statistic:.2f}", "📐")
    with c2:
        metric_card("p-valor", p_display, "📊")
    with c3:
        metric_card("Graus de liberdade", str(chi2.degrees_of_freedom), "🧮")

    if chi2.p_value >= 0.05:
        st.success(f"✅ {chi2.interpretation}")
    else:
        st.warning(f"⚠️ {chi2.interpretation}")


# =========================
# PROBABILIDADE MATEMÁTICA
# =========================
section("🎲 Probabilidade Matemática")

st.markdown(
    "Cálculo baseado em **combinatória C(n,k)** por modalidade — não em frequência histórica."
)

col_input, col_output = st.columns([1, 1])

with col_input:
    qtd_apostas = st.slider("🎟️ Quantidade de apostas", min_value=1, max_value=100, value=1)

    # O máximo de dezenas por aposta é o limite de desdobramento com preço
    # definido na price_table (não o universo), evitando selecionar uma
    # quantidade sem preço/probabilidade válida.
    price_dezenas = sorted(config["price_table"].keys())
    min_dezenas = min(price_dezenas)
    max_dezenas = min(max(price_dezenas), config["universo"])

    if max_dezenas <= min_dezenas:
        qtd_dezenas = min_dezenas
        st.info(f"🎯 Nesta loteria, a quantidade de dezenas é fixa: **{qtd_dezenas} dezenas**.")
    else:
        qtd_dezenas = st.slider(
            "🔢 Quantidade de dezenas por aposta",
            min_value=min_dezenas,
            max_value=max_dezenas,
            value=min_dezenas,
            help=f"Desdobramento de {min_dezenas} a {max_dezenas} dezenas (conforme a tabela de preços).",
        )

prob_single = win_probability(lottery_cfg, qtd_dezenas, qtd_apostas=1)
prob_total = win_probability(lottery_cfg, qtd_dezenas, qtd_apostas)
ev_result = calculate_expected_value(lottery_cfg, qtd_dezenas, qtd_apostas)

custo_por_aposta = config["price_table"].get(qtd_dezenas)
if custo_por_aposta is None:
    st.error(f"Preço não disponível para {qtd_dezenas} dezenas nesta modalidade.")
    st.stop()

custo_total = custo_por_aposta * qtd_apostas

with col_output:
    c1, c2 = st.columns(2)

    with c1:
        metric_card("Probabilidade por aposta", f"{prob_single.probability:.10%}", "🎯")
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        metric_card("Custo por aposta", _format_brl(custo_por_aposta), "💰")

    with c2:
        metric_card("Probabilidade total", f"{prob_total.probability:.10%}", "📈")
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        metric_card("Custo total", _format_brl(custo_total), "💸")

st.caption(
    f"Fórmula: {prob_single.formula} | Total de combinações: {prob_single.total_combinations:,}"
)


# =========================
# VALOR ESPERADO / VANTAGEM DA CASA
# =========================
section("💸 Valor Esperado e Vantagem da Casa")

st.markdown(
    """
    O **valor esperado (EV)** mede quanto você recupera em média por aposta.
    Em loterias, o EV é **negativo**: a diferença vai para premiação, tributos e margem da operadora.
    """
)

ev_col1, ev_col2, ev_col3 = st.columns(3)

with ev_col1:
    metric_card(
        f"P({ev_result.main_tier.name})",
        f"{ev_result.main_tier.probability:.10%}",
        "🎯",
    )

with ev_col2:
    metric_card("Custo da aposta", _format_brl(ev_result.cost), "💰")

with ev_col3:
    if ev_result.has_prize_data and ev_result.expected_value is not None:
        metric_card("Valor esperado (EV)", _format_brl(ev_result.expected_value), "📉")
    else:
        metric_card("Valor esperado (EV)", "Indisponível", "📉")

if ev_result.has_prize_data and ev_result.expected_return is not None:
    st.markdown(
        f"""
        - Retorno esperado: **{_format_brl(ev_result.expected_return)}**
        - Vantagem da casa: **{ev_result.house_edge_pct:.2f}%**
        - {ev_result.note}
        """
    )
    st.error(
        f"⚠️ EV negativo de **{_format_brl(ev_result.expected_value)}** por aposta "
        f"(referência com prêmio médio estimado)."
    )
else:
    st.info(ev_result.note)


# =========================
# FREQUÊNCIA DAS DEZENAS
# =========================
section("📈 Frequência das Dezenas")

fig_bar = px.bar(
    freq_df,
    x="Dezena",
    y="Frequência",
    color="Frequência",
    color_continuous_scale=[[0, config["color"]], [1, "#111827"]],
    title=f"Frequência histórica — {lottery_name}",
)

fig_bar.update_layout(height=450, coloraxis_showscale=False)

st.plotly_chart(fig_bar, use_container_width=True)


# =========================
# TOP & BOTTOM
# =========================
section("🍩 Top & Bottom Dezenas")

top_n = min(config["total_bolas"], len(freq)) if not freq.empty else 0

if top_n > 0:
    top = freq.sort_values(ascending=False).head(top_n)
    bottom = freq.sort_values().head(top_n)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_top = go.Figure(
            data=[go.Pie(labels=top.index.astype(str), values=top.values, hole=0.5)]
        )
        fig_top.update_layout(title=f"🔥 Top {top_n} Mais Sorteadas — {lottery_name}", height=400)
        st.plotly_chart(fig_top, use_container_width=True)

    with col_right:
        fig_bottom = go.Figure(
            data=[go.Pie(labels=bottom.index.astype(str), values=bottom.values, hole=0.5)]
        )
        fig_bottom.update_layout(
            title=f"❄️ Top {top_n} Menos Sorteadas — {lottery_name}", height=400
        )
        st.plotly_chart(fig_bottom, use_container_width=True)

    st.warning(
        "Dezenas mais ou menos sorteadas no passado **não são sinais** para o futuro. "
        "Cada sorteio é independente."
    )


# =========================
# PROBABILIDADE EMPÍRICA
# =========================
section("🎯 Probabilidade Empírica")

st.dataframe(prob_df.style.format({"Probabilidade": "{:.4%}"}), use_container_width=True)


# =========================
# ANÁLISES ESPECÍFICAS POR MODALIDADE
# =========================
extra_fields = config.get("extra_fields") or {}
show_trevos = "trevos" in extra_fields and extra_field_frequency(df, "trevos").size > 0
show_draws = bool(config.get("multiple_draws")) and "draw_index" in df.columns
show_supersete = config.get("special_handler") == "supersete"
time_field = next(
    (f for f in extra_fields if f != "trevos" and not str(f).endswith("_universo")),
    None,
)
show_time = bool(time_field) and extra_field_frequency(df, time_field).size > 0

if show_trevos or show_draws or show_supersete or show_time:
    section("🧩 Análises Específicas desta Modalidade")
    st.caption(
        "Complementos além da frequência clássica das dezenas. "
        "Histórico ≠ previsão: cada sorteio continua independente."
    )
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    if show_trevos:
        trevo_freq = extra_field_frequency(df, "trevos")
        if not trevo_freq.empty:
            trevo_df = trevo_freq.reset_index()
            trevo_df.columns = ["Trevo", "Frequência"]
            fig_trevos = px.bar(
                trevo_df,
                x="Trevo",
                y="Frequência",
                title=f"Frequência dos trevos — {lottery_name}",
                color="Frequência",
                color_continuous_scale=[[0, config["color"]], [1, "#111827"]],
            )
            fig_trevos.update_layout(height=400, coloraxis_showscale=False)
            st.plotly_chart(fig_trevos, use_container_width=True)

    if show_draws:
        by_draw = frequency_by_draw(df, total_bolas=config["total_bolas"])
        if by_draw:
            cols = st.columns(len(by_draw))
            for col, (draw_id, series) in zip(cols, sorted(by_draw.items()), strict=False):
                draw_df = series.reset_index()
                draw_df.columns = ["Dezena", "Frequência"]
                fig_draw = px.bar(
                    draw_df,
                    x="Dezena",
                    y="Frequência",
                    title=f"Sorteio {draw_id}",
                    color_discrete_sequence=[config["color"]],
                )
                fig_draw.update_layout(height=380)
                with col:
                    st.plotly_chart(fig_draw, use_container_width=True)

    if show_supersete:
        pos_df = frequency_by_position(df, n_positions=config["total_bolas"])
        if not pos_df.empty:
            pivot = pos_df.pivot(index="digito", columns="coluna", values="frequencia").fillna(0)
            fig_heat = px.imshow(
                pivot,
                labels={"x": "Coluna", "y": "Dígito", "color": "Frequência"},
                title=f"Frequência por coluna — {lottery_name}",
                aspect="auto",
                color_continuous_scale="Blues",
            )
            fig_heat.update_layout(height=420)
            st.plotly_chart(fig_heat, use_container_width=True)

    if show_time and time_field:
        time_freq = extra_field_frequency(df, time_field)
        top_n = min(15, len(time_freq))
        top = time_freq.head(top_n).sort_values(ascending=True)
        time_df = top.reset_index()
        time_df.columns = ["Time", "Frequência"]
        fig_time = px.bar(
            time_df,
            x="Frequência",
            y="Time",
            orientation="h",
            title=f"Top {top_n} — Time do Coração",
            color="Frequência",
            color_continuous_scale=[[0, config["color"]], [1, "#111827"]],
        )
        fig_time.update_layout(height=max(360, top_n * 28), coloraxis_showscale=False)
        st.plotly_chart(fig_time, use_container_width=True)


# =========================
# EXPORTAR RELATÓRIO PDF
# =========================
section("📥 Exportar Relatório")

st.markdown(
    "Gera um PDF com resumo (KPIs), ranking das dezenas e probabilidade empírica. "
    "O gráfico de frequência entra quando Kaleido/Chrome está disponível; "
    "caso contrário o relatório segue só com tabelas."
)
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

_pdf_state_key = "stats_pdf_bytes"
_pdf_lottery_key = "stats_pdf_lottery_key"

if st.session_state.get(_pdf_lottery_key) != config["key"]:
    st.session_state.pop(_pdf_state_key, None)
    st.session_state[_pdf_lottery_key] = config["key"]

if freq.empty:
    st.info("Não há dados de frequência suficientes para gerar o relatório PDF.")
else:
    col_gerar, col_baixar = st.columns([1, 1])

    with col_gerar:
        if st.button("📄 Gerar PDF", key=f"gerar_pdf_{config['key']}", use_container_width=True):
            try:
                with st.spinner("Gerando relatório PDF..."):
                    buffer = generate_statistics_pdf(
                        df,
                        total_bolas=config["total_bolas"],
                        titulo=f"Relatório Estatístico — {lottery_name}",
                    )
                    st.session_state[_pdf_state_key] = buffer.getvalue()
                st.success("Relatório pronto. Use o botão ao lado para baixar.")
            except Exception as exc:
                st.session_state.pop(_pdf_state_key, None)
                st.error(f"Não foi possível gerar o PDF.\n\n{exc}")

    with col_baixar:
        if st.session_state.get(_pdf_state_key):
            st.download_button(
                "⬇️ Baixar relatório PDF",
                data=st.session_state[_pdf_state_key],
                file_name=f"relatorio_{config['key']}.pdf",
                mime="application/pdf",
                key=f"download_pdf_{config['key']}",
                use_container_width=True,
            )
        else:
            st.caption("Gere o PDF primeiro para habilitar o download.")


# =========================
# OBSERVAÇÕES
# =========================
section("⚠️ Observações Importantes")

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
st.info(
    f"""
- {lottery_name} é um jogo **totalmente aleatório**
- Frequência histórica **não influencia sorteios futuros**
- Estatística **não aumenta a chance real de ganhar**
- Dezenas quentes/frias são **ruído**, não previsão

Este painel é **educacional e analítico**.
"""
)

responsible_gaming_footer()
