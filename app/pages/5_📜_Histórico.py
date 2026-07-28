import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

from app.core.lotteries import LOTTERIES
from app.services.dataset import load_dataset
from app.services.user_history import (
    clear_user_games,
    delete_user_game,
    export_history_csv,
    list_user_games,
)
from app.services.validator import check_game
from app.ui.shell import render_app_chrome
from app.ui.theme import page_title, responsible_gaming_footer, section

st.set_page_config(page_title="Histórico de Jogos", layout="wide")

render_app_chrome(show_lottery=True)

page_title(
    "📜 Histórico de Jogos",
    "Jogos salvos nesta instalação (SQLite local) — sem conta de usuário",
)

section("🔎 Filtro")

lottery_options = ["Todas"] + list(LOTTERIES.keys())
filter_name = st.selectbox("Loteria", lottery_options, key="history_lottery_filter")

lottery_key_filter = None
if filter_name != "Todas":
    lottery_key_filter = LOTTERIES[filter_name]["key"]

rows = list_user_games(lottery_key_filter, limit=200)

section("📋 Jogos salvos")

if not rows:
    st.info(
        "Nenhum jogo no histórico ainda. Salve a partir de **Verificação** ou **Combinações Inéditas**."
    )
    responsible_gaming_footer()
    st.stop()

name_by_key = {cfg["key"]: name for name, cfg in LOTTERIES.items()}

display_rows = []
for row in rows:
    extras = row.get("extras") or {}
    extras_txt = (
        "; ".join(f"{k}: {', '.join(str(v) for v in vals)}" for k, vals in extras.items())
        if extras
        else "—"
    )
    display_rows.append(
        {
            "ID": row["id"],
            "Data": row["created_at"],
            "Loteria": name_by_key.get(row["lottery_key"], row["lottery_key"]),
            "Dezenas": ", ".join(str(n) for n in row["dezenas"]),
            "Extras": extras_txt,
            "Origem": row["source"],
            "Nota": row.get("note") or "",
        }
    )

st.dataframe(display_rows, use_container_width=True, hide_index=True)

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

col_export, col_clear = st.columns(2)

with col_export:
    try:
        csv_bytes = export_history_csv(rows)
        st.download_button(
            "⬇️ Baixar histórico (CSV)",
            data=csv_bytes,
            file_name="historico_jogos.csv",
            mime="text/csv",
            use_container_width=True,
        )
    except ValueError as exc:
        st.caption(str(exc))

with col_clear:
    if st.button("🗑️ Limpar histórico filtrado", use_container_width=True):
        removed = clear_user_games(lottery_key_filter)
        st.success(f"{removed} jogo(s) removido(s).")
        st.rerun()

section("⚙️ Ações por jogo")

ids = [row["id"] for row in rows]
selected_id = st.selectbox("Selecione um ID", ids, key="history_selected_id")
selected = next(r for r in rows if r["id"] == selected_id)

c1, c2 = st.columns(2)

with c1:
    if st.button("🔍 Verificar novamente", use_container_width=True):
        try:
            cfg = next(c for c in LOTTERIES.values() if c["key"] == selected["lottery_key"])
            df = load_dataset(
                lottery_key=cfg["key"],
                total_bolas=cfg["total_bolas"],
                extra_fields=cfg.get("extra_fields"),
                multiple_draws=cfg.get("multiple_draws", False),
                special_handler=cfg.get("special_handler"),
            )
            extras = selected.get("extras") or None
            found = check_game(selected["dezenas"], df, extra_values=extras or None)
            if found:
                st.success("Este jogo **já foi sorteado** no histórico da Caixa.")
            else:
                st.warning("Este jogo **nunca foi sorteado** no histórico carregado.")
        except (FileNotFoundError, ValueError, StopIteration) as exc:
            st.error(f"Não foi possível verificar.\n\n{exc}")

with c2:
    if st.button("🗑️ Apagar este jogo", use_container_width=True):
        if delete_user_game(selected_id):
            st.success(f"Jogo #{selected_id} removido.")
            st.rerun()
        else:
            st.error("Jogo não encontrado.")

responsible_gaming_footer()
