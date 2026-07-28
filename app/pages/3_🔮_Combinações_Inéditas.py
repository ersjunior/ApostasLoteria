import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

from app.combinations.generator import generate_unique_combinations
from app.services.dataset import load_dataset
from app.services.exporter import export_csv
from app.services.user_history import SOURCE_COMBINATIONS, add_user_games
from app.ui.shell import render_app_chrome, render_lottery_picker
from app.ui.theme import game_card, lottery_badge, page_title, responsible_gaming_footer, section

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Combinações Inéditas", layout="wide")

render_app_chrome()


def pastel_color(hex_color: str, alpha=0.15):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


page_title(
    "🔮 Gerador de Combinações Inéditas",
    "Sorteio aleatório de combinações que ainda não apareceram no histórico — sem poder preditivo",
)
lottery_name, config = render_lottery_picker()
lottery_badge(
    lottery_name,
    config,
    detail=f"Combinações com <b>{config['total_bolas']} dezenas</b>.",
)
st.info(
    "⚠️ As combinações abaixo são geradas por **sorteio aleatório uniforme**. "
    "Não há modelo de machine learning nem capacidade de previsão — apenas combinações "
    "inéditas em relação ao histórico carregado."
)

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
# GERAÇÃO
# =========================
section("✨ Gerar Combinações")

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

_games_key = f"combo_games_{config['key']}"

n_games = st.slider(
    "Quantidade de jogos",
    min_value=1,
    max_value=100,
    value=10,
    key="combo_n_games",
)

_plural = "s" if n_games > 1 else ""

if st.button(f"{config['icon']} Gerar {n_games} Jogo{_plural} Inédito{_plural}"):
    st.session_state[_games_key] = generate_unique_combinations(
        df=df,
        n_games=n_games,
        universo=config["universo"],
        total_bolas=config["total_bolas"],
        extra_fields=config.get("extra_fields"),
    )

games = st.session_state.get(_games_key) or []

if games:
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
                        extras=games[game_index].get("extras"),
                    )
                game_index += 1

    section("📥 Exportar / Histórico")

    csv = export_csv(games)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    col_csv, col_hist = st.columns(2)

    with col_csv:
        st.download_button(
            "📄 Baixar jogos em CSV",
            csv,
            f"combinacoes_ineditas_{config['key']}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_hist:
        if st.button(
            "💾 Salvar no histórico",
            key=f"save_combo_{config['key']}",
            use_container_width=True,
        ):
            try:
                ids = add_user_games(
                    config["key"],
                    games,
                    source=SOURCE_COMBINATIONS,
                    note=f"Combinações inéditas — {lottery_name}",
                )
                st.success(f"{len(ids)} jogo(s) salvos no histórico local.")
            except Exception as exc:
                st.error(f"Não foi possível salvar no histórico.\n\n{exc}")

responsible_gaming_footer()
