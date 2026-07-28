import sys
from math import comb
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
from app.services.statistics import empirical_probability, frequency
from app.ui.theme import metric_card, page_title, section
from app.ui.theme_manager import apply_theme, init_theme

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Estatísticas das Loterias", layout="wide")


init_theme()
apply_theme()


# =========================
# SELETOR DE LOTERIA
# =========================
page_title("📊 Estatísticas das Loterias", "Análise histórica e estatística dos sorteios")

section("🎲 Seleção da Loteria")

lottery_name = st.selectbox("Escolha a loteria", list(LOTTERIES.keys()))

config = LOTTERIES[lottery_name]


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
# PROBABILIDADE MATEMÁTICA
# =========================
section("🎲 Probabilidade Matemática")

st.markdown("Cálculo baseado em **combinações matemáticas reais**, não em frequência histórica.")

col_input, col_output = st.columns([1, 1])

with col_input:
    qtd_apostas = st.slider("🎟️ Quantidade de apostas", min_value=1, max_value=100, value=1)

    # =========================
    # DEFINIÇÃO DE DEZENAS POR APOSTA
    # =========================
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

# Cálculo
total_combinacoes = comb(config["universo"], config["total_bolas"])
combinacoes_aposta = comb(qtd_dezenas, config["total_bolas"])

prob_por_aposta = combinacoes_aposta / total_combinacoes
prob_total = 1 - (1 - prob_por_aposta) ** qtd_apostas

custo_por_aposta = config["price_table"][qtd_dezenas]
custo_total = custo_por_aposta * qtd_apostas

with col_output:
    c1, c2 = st.columns(2)

    with c1:
        metric_card("Probabilidade por aposta", f"{prob_por_aposta:.10%}", "🎯")
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        metric_card(
            "Custo por aposta",
            f"R$ {custo_por_aposta:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "💰",
        )

    with c2:
        metric_card("Probabilidade total", f"{prob_total:.10%}", "📈")
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        metric_card(
            "Custo total",
            f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "💸",
        )


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

top_n = min(config["total_bolas"], len(freq))

top = freq.sort_values(ascending=False).head(top_n)
bottom = freq.sort_values().head(top_n)

col_left, col_right = st.columns(2)

with col_left:
    fig_top = go.Figure(data=[go.Pie(labels=top.index.astype(str), values=top.values, hole=0.5)])
    fig_top.update_layout(title=f"🔥 Top {top_n} Mais Sorteadas — {lottery_name}", height=400)
    st.plotly_chart(fig_top, use_container_width=True)

with col_right:
    fig_bottom = go.Figure(
        data=[go.Pie(labels=bottom.index.astype(str), values=bottom.values, hole=0.5)]
    )
    fig_bottom.update_layout(title=f"❄️ Top {top_n} Menos Sorteadas — {lottery_name}", height=400)
    st.plotly_chart(fig_bottom, use_container_width=True)


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

Este painel é **educacional e analítico**.
"""
)
