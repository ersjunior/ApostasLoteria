import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

from app.combinations.generator import generate_unique_combinations
from app.core.lotteries import LOTTERIES
from app.services.dataset import load_dataset
from app.services.exporter import export_csv
from app.ui.theme import game_card, page_title, section
from app.ui.theme_manager import apply_theme, init_theme

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Combinações Inéditas", layout="wide")

init_theme()
apply_theme()


# =========================
# FUNÇÃO COR PASTEL
# =========================
def pastel_color(hex_color: str, alpha=0.15):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


# =========================
# TÍTULO
# =========================
page_title(
    "🔮 Gerador de Combinações Inéditas",
    "Sorteio aleatório de combinações que ainda não apareceram no histórico — sem poder preditivo",
)

# =========================
# SELETOR DE LOTERIA
# =========================
section("🎲 Seleção da Loteria")
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
st.info(
    "⚠️ As combinações abaixo são geradas por **sorteio aleatório uniforme**. "
    "Não há modelo de machine learning nem capacidade de previsão — apenas combinações "
    "inéditas em relação ao histórico carregado."
)

lottery_name = st.selectbox("Escolha a loteria", list(LOTTERIES.keys()))

config = LOTTERIES[lottery_name]

st.markdown(
    f"""
    <div style="
        margin-top:10px;
        padding:10px 15px;
        border-left:5px solid {config["color"]};
        background-color:{pastel_color(config["color"])};
        border-radius:6px;
    ">
        <strong>{config["icon"]} {lottery_name}</strong><br>
        Combinações com <b>{config["total_bolas"]} dezenas</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

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
# GERAÇÃO
# =========================
section("✨ Gerar Combinações")

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

if st.button(f"{config['icon']} Gerar 10 Jogos Inéditos"):
    games = generate_unique_combinations(
        df=df,
        n_games=10,
        universo=config["universo"],
        total_bolas=config["total_bolas"],
        extra_fields=config.get("extra_fields"),
    )

    section("📋 Jogos Gerados")

    COLS_PER_ROW = 3
    game_index = 0

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    for _row in range((len(games) + COLS_PER_ROW - 1) // COLS_PER_ROW):
        cols = st.columns(COLS_PER_ROW)

        for col in cols:
            if game_index < len(games):
                with col:
                    game_card(
                        title=f"{config['icon']} Jogo {game_index + 1}",
                        numbers=games[game_index]["dezenas"],
                        status="❌ Nunca sorteado",
                        accent_color=config["color"],
                        background_color=pastel_color(config["color"]),
                    )
                game_index += 1

    # =========================
    # EXPORTAÇÃO
    # =========================
    section("📥 Exportar Jogos")

    csv = export_csv(games)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    st.download_button(
        "📄 Baixar jogos em CSV",
        csv,
        f"combinacoes_ineditas_{config['key']}.csv",
        mime="text/csv",
    )
