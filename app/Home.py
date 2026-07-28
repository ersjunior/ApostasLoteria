import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.core.lotteries import LOTTERIES
from app.services.dataset import enrich_dataset, normalize_columns
from app.ui.theme import card, page_title, section
from app.ui.theme_manager import apply_theme, init_theme

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="🍀 Loterias Analyzer", layout="wide")

init_theme()
apply_theme()

# =========================
# HERO / HEADER
# =========================
page_title(
    "🎰 Loterias Analyzer",
    "Análise estatística, verificação de jogos e geração de combinações inéditas para loterias",
)

st.markdown(
    """
    <div style="margin-top:10px; font-size:16px; color:#9ca3af;">
        Uma plataforma analítica e educacional para estudo de jogos de loteria,
        baseada em dados oficiais, estatística descritiva e simulações matemáticas.
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# VISÃO GERAL
# =========================
section("📌 O que este sistema oferece")

st.markdown("<div style='margin-top:25px'></div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    card(
        "🎯 Verificação de Jogos",
        "Verifique múltiplos jogos simultaneamente e descubra se combinações já foram sorteadas.",
    )

with col2:
    card(
        "🔮 Combinações Inéditas", "Gere jogos aleatórios que nunca foram sorteados anteriormente."
    )

with col3:
    card(
        "📊 Estatísticas Avançadas",
        "Explore frequências, probabilidades empíricas e distribuição das dezenas.",
    )

with col4:
    card(
        "💰Custos e Probabilidades",
        "Simule diferentes cenários de apostas, custos totais e probabilidades matemáticas reais.",
    )

# =========================
# LOTERIAS SUPORTADAS
# =========================
section("🎲 Loterias suportadas")

st.markdown(
    """
    O sistema foi projetado para funcionar de forma **genérica**, suportando diferentes modalidades
    de loteria com regras próprias.\n
    ***Apenas Mega-Sena e Lotofácil atualmente, mas extensível para outros tipos de loterias.***
    """
)

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    card(
        "Mega-Sena",
        "A mais popular loteria do Brasil, com análise completa de estatísticas, verificação "
        "e geração de jogos inéditos.",
    )

with c2:
    card(
        "Lotofácil",
        "Análises específicas para apostas com 15 a 20 dezenas, incluindo simulações de custo "
        "e probabilidade.",
    )

with c3:
    card(
        "Extensível",
        "Arquitetura preparada para inclusão de novas loterias, como Quina, Lotomania e outras.",
    )

# =========================
# COMO UTILIZAR
# =========================
section("🧭 Como utilizar a aplicação")

st.markdown(
    """
    ### 1️⃣ Obtenha a base de dados oficial
    Baixe o arquivo **XLSX oficial** da loteria desejada diretamente do site da Caixa Econômica Federal.

    ### 2️⃣ Faça o upload dos arquivos
    Utilize o painel lateral para enviar os arquivos baixado ao sistema.

    ### 3️⃣ Selecione a loteria
    Nas páginas de **Verificação**, **Forecast** e **Estatísticas**, escolha a modalidade desejada.

    ### 4️⃣ Explore as funcionalidades
    Analise dados históricos, gere jogos inéditos e simule cenários de apostas.
    """
)

# =========================
# TECNOLOGIAS
# =========================
section("⚙️ Tecnologias utilizadas")

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
st.markdown(
    """
    - 🐍 **Python**
    - 📊 **Pandas & NumPy**
    - 📈 **Plotly**
    - 🎨 **Streamlit**
    - 🧮 **Estatística combinatória**
    - 📁 **Bases oficiais XLSX da Caixa Econômica Federal**
    """
)

# =========================
# AVISO LEGAL
# =========================
st.info(
    """
    ⚠️ **Aviso importante**
    Este sistema possui finalidade **educacional e analítica**.
    Jogos de loteria são eventos **aleatórios**, e análises estatísticas **não garantem prêmios**.
    """
)

# =========================
# UPLOAD MANUAL (SEÇÃO ISOLADA)
# =========================
st.sidebar.markdown("## 📤 Upload Manual do XLSX")

# 🔹 SELETOR APENAS AQUI
loteria_upload = st.sidebar.selectbox(
    "🎰 Loteria do arquivo",
    list(LOTTERIES.keys()),
    help="Selecione a loteria correspondente ao arquivo XLSX",
)

st.sidebar.markdown(
    """
    <div style="
        font-size: 13px;
        line-height: 1.4;
        color: #9ca3af;
        margin-top: -10px;
        margin-bottom: 10px;
    ">
        Use esta opção apenas após baixar o arquivo XLSX oficial.
        Informe corretamente a loteria correspondente.
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.sidebar.file_uploader(
    "📄 Envie o arquivo XLSX", type=["xlsx"], help="Arquivo oficial baixado do site da Caixa"
)

if uploaded_file is not None:
    config = LOTTERIES[loteria_upload]

    try:
        df = pd.read_excel(uploaded_file)
        df = normalize_columns(df)
        df = enrich_dataset(df, config["total_bolas"])

        df.to_excel(config["file_path"], index=False)
        st.cache_data.clear()

        st.sidebar.success(f"✅ Base da **{loteria_upload}** carregada com sucesso!")

    except Exception as e:
        st.sidebar.error(f"❌ Erro ao processar o arquivo: {str(e)}")

# =========================
# SIDEBAR — BASE DE DADOS
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("## 📥 Base de Dados Oficial")

st.sidebar.markdown(
    """
    <div style="
        font-size: 14px;
        line-height: 1.4;
        color: #9ca3af;
        margin-bottom: 8px;
    ">
        Para utilizar o sistema, é necessário baixar a base oficial da loteria desejada
        diretamente do site da Caixa Econômica Federal.
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.link_button(
    "⬇️ Baixar base atualizada", "https://loterias.caixa.gov.br/", use_container_width=True
)

st.sidebar.caption(
    "No site da Caixa, selecione a loteria desejada e clique em **Download dos resultados**."
)

# =============================
# VALIDAÇÃO DAS BASES
# =============================
section("📂 Status das Bases")
st.markdown("<div style='margin-top:25px'></div>", unsafe_allow_html=True)
COLS_PER_ROW = 5
items = list(LOTTERIES.items())

for i in range(0, len(items), COLS_PER_ROW):
    cols = st.columns(COLS_PER_ROW)

    for col, (name, cfg) in zip(cols, items[i : i + COLS_PER_ROW], strict=False):
        with col:
            if Path(cfg["file_path"]).exists():
                st.success(f"✅ {name}")
            else:
                st.warning(f"⚠️ {name}")

st.cache_data.clear()
