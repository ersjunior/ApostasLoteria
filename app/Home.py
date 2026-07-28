import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.config import configure_runtime
from app.core.lotteries import LOTTERIES
from app.services.dataset import get_lottery_cache_status, persist_dataset
from app.ui.lottery_selector import lottery_selector
from app.ui.shell import render_app_chrome
from app.ui.theme import card, page_title, responsible_gaming_footer, section
from loterias_core.schema import DatasetSchemaError

configure_runtime()

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="🍀 Loterias Analyzer", layout="wide")

render_app_chrome(show_lottery=True)

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
        footer="📄 Página 🎯 Verificação",
    )

with col2:
    card(
        "🔮 Combinações Inéditas",
        "Gere jogos aleatórios que nunca foram sorteados anteriormente.",
        footer="📄 Página 🔮 Combinações Inéditas",
    )

with col3:
    card(
        "📊 Estatísticas Avançadas",
        "Explore frequências, probabilidades empíricas e distribuição das dezenas.",
        footer="📄 Página 📊 Estatísticas",
    )

with col4:
    card(
        "💰 Custos e Probabilidades",
        "Simule cenários de apostas, custos totais, valor esperado e probabilidades reais.",
        footer="📊 Seção da página Estatísticas",
    )

# =========================
# LOTERIAS SUPORTADAS
# =========================
section("🎲 Loterias suportadas")

n_modalidades = len(LOTTERIES)
st.markdown(
    f"""
    O sistema funciona de forma **genérica** para **{n_modalidades} modalidades**,
    cada uma com regras, universo e preços próprios.
    """
)


def _lottery_card_description(cfg: dict) -> str:
    parts = [f"{cfg['total_bolas']} dezenas · universo {cfg['universo']}"]
    if cfg.get("multiple_draws"):
        parts.append("2 sorteios por concurso")
    if cfg.get("extra_fields"):
        playable = [k for k in cfg["extra_fields"] if not k.endswith("_universo")]
        if playable:
            parts.append(", ".join(playable))
    elif "trevo" in (cfg.get("placeholder") or "").lower():
        parts.append("2 trevos")
    return " · ".join(parts)


st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
LOTTERY_COLS = 3
lottery_items = list(LOTTERIES.items())

for i in range(0, len(lottery_items), LOTTERY_COLS):
    cols = st.columns(LOTTERY_COLS)
    for col, (name, cfg) in zip(cols, lottery_items[i : i + LOTTERY_COLS], strict=False):
        with col:
            card(f"{cfg['icon']} {name}", _lottery_card_description(cfg))

# =========================
# COMO UTILIZAR
# =========================
section("🧭 Como utilizar a aplicação")

st.markdown(
    """
    ### 1️⃣ Obtenha a base de dados oficial
    Baixe o arquivo **XLSX oficial** da loteria desejada diretamente do site da Caixa Econômica Federal.

    ### 2️⃣ Faça o upload dos arquivos
    Utilize o painel lateral para enviar os arquivos baixados ao sistema.

    ### 3️⃣ Selecione a loteria e o tema
    No **painel lateral (Controles)**, escolha a modalidade e o tema claro/escuro —
    a preferência permanece ao navegar entre as páginas.

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
loteria_upload, _ = lottery_selector(
    "🎰 Loteria do arquivo",
    key="upload_lottery",
    help="Selecione a loteria correspondente ao arquivo XLSX",
    sidebar=True,
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
    config = {**LOTTERIES[loteria_upload], "name": loteria_upload}

    try:
        df = pd.read_excel(uploaded_file)
        persist_dataset(df, config, lottery_name=loteria_upload)
        st.cache_data.clear()

        st.sidebar.success(f"✅ Base da **{loteria_upload}** carregada com sucesso!")

    except DatasetSchemaError as e:
        st.sidebar.error(str(e))
    except Exception as e:
        st.sidebar.error(
            f"❌ Erro ao processar o arquivo.\n\n{e}\n\n"
            "Verifique se o XLSX é o arquivo oficial da modalidade selecionada."
        )

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

cache_status = get_lottery_cache_status()
loaded_count = sum(
    1 for cfg in LOTTERIES.values() if cache_status.get(cfg["key"], {}).get("exists")
)

if loaded_count == 0:
    st.warning(
        "⚠️ **Nenhuma base carregada ainda.**\n\n"
        "Faça upload do XLSX oficial no painel lateral ou use a API (`POST /dataset/`) "
        "para popular o banco SQLite na primeira execução."
    )

COLS_PER_ROW = 5
items = list(LOTTERIES.items())

for i in range(0, len(items), COLS_PER_ROW):
    cols = st.columns(COLS_PER_ROW)

    for col, (name, cfg) in zip(cols, items[i : i + COLS_PER_ROW], strict=False):
        with col:
            status = cache_status.get(cfg["key"], {})
            if status.get("exists"):
                last = status.get("last_concurso")
                total = status.get("total_records", 0)
                detail = (
                    f" — concurso {last}, {total} registros" if last else f" — {total} registros"
                )
                st.success(f"✅ {name}{detail}")
            else:
                st.warning(f"⚠️ {name}")

responsible_gaming_footer()
