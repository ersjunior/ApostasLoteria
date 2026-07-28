import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.core.lotteries import LOTTERIES
from app.services.dataset import load_dataset
from app.services.statistics import chi_square_uniformity_test, empirical_probability, frequency
from app.ui.theme import metric_card, page_title, section
from app.ui.theme_manager import apply_theme, init_theme
from loterias_core.combinatorics import get_lottery_config_from_dict, win_probability
from loterias_core.expected_value import calculate_expected_value

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Estatísticas das Loterias", layout="wide")


init_theme()
apply_theme()


def _format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# =========================
# SELETOR DE LOTERIA
# =========================
page_title("📊 Estatísticas das Loterias", "Análise histórica e estatística dos sorteios")

section("🎲 Seleção da Loteria")

lottery_name = st.selectbox("Escolha a loteria", list(LOTTERIES.keys()))

config = LOTTERIES[lottery_name]
lottery_cfg = get_lottery_config_from_dict(config)


# =========================
# CARREGAMENTO DO DATASET
# =========================
try:
    df = load_dataset(
        file_path=config["file_path"],
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
        "⚠️ Esta loteria possui uma estrutura especial.\n\n"
        "As estatísticas de frequência clássicas não se aplicam.\n"
        "Em breve, análises específicas serão adicionadas."
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

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Estatística χ²", f"{chi2.statistic:.4f}", "📐")
    with c2:
        metric_card("p-valor", f"{chi2.p_value:.4f}", "📊")
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

    if config["total_bolas"] >= config["universo"]:
        qtd_dezenas = config["total_bolas"]
        st.info(f"🎯 Nesta loteria, a quantidade de dezenas é fixa: **{qtd_dezenas} dezenas**.")
    else:
        qtd_dezenas = st.slider(
            "🔢 Quantidade de dezenas por aposta",
            min_value=config["total_bolas"],
            max_value=config["universo"],
            value=config["total_bolas"],
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
