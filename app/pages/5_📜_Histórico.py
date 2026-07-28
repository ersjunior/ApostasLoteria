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

render_app_chrome()

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

# Descarta resultados de verificação em lote quando o filtro de loteria muda,
# evitando exibir análises que já não correspondem à listagem atual.
if st.session_state.get("history_bulk_filter") != filter_name:
    st.session_state.pop("history_bulk_results", None)
    st.session_state["history_bulk_filter"] = filter_name

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
        st.session_state.pop("history_bulk_results", None)
        st.success(f"{removed} jogo(s) removido(s).")
        st.rerun()

section("🔍 Verificar jogos salvos")

st.caption(
    "Confere, em lote, quais jogos salvos já foram sorteados — processados por ordem "
    "de ID (crescente)."
)
st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

max_verificaveis = min(100, len(rows))

if max_verificaveis == 1:
    qtd_verificar = 1
    st.info("Há apenas **1 jogo** salvo — a verificação conferirá esse jogo.")
else:
    qtd_verificar = st.slider(
        "Quantidade de jogos a verificar",
        min_value=1,
        max_value=max_verificaveis,
        value=min(10, max_verificaveis),
        key="history_verify_qtd",
        help=(
            f"Escolha livremente de 1 a {max_verificaveis} jogo(s). "
            "Serão verificados os primeiros por ordem de ID."
        ),
    )

_plural = "s" if qtd_verificar > 1 else ""
if st.button(
    f"🔍 Verificar {qtd_verificar} jogo{_plural}",
    use_container_width=True,
    key="history_bulk_verify_btn",
):
    ordenados = sorted(rows, key=lambda r: r["id"])[:qtd_verificar]
    resultados: list[tuple[str, str, str, str]] = []
    datasets: dict[str, object] = {}

    for row in ordenados:
        lk = row["lottery_key"]
        titulo = f"#{row['id']} · {name_by_key.get(lk, lk)}"
        dezenas_txt = ", ".join(str(n) for n in row["dezenas"])

        if lk not in datasets:
            try:
                cfg = next(c for c in LOTTERIES.values() if c["key"] == lk)
                datasets[lk] = load_dataset(
                    lottery_key=cfg["key"],
                    total_bolas=cfg["total_bolas"],
                    extra_fields=cfg.get("extra_fields"),
                    multiple_draws=cfg.get("multiple_draws", False),
                    special_handler=cfg.get("special_handler"),
                )
            except (FileNotFoundError, ValueError, StopIteration) as exc:
                datasets[lk] = exc

        base = datasets[lk]
        if isinstance(base, Exception):
            resultados.append(("error", titulo, dezenas_txt, "Base indisponível"))
            continue

        try:
            extras = row.get("extras") or None
            found = check_game(row["dezenas"], base, extra_values=extras or None)
            if found:
                resultados.append(("success", titulo, dezenas_txt, "Já sorteado 🎉"))
            else:
                resultados.append(("warning", titulo, dezenas_txt, "Nunca sorteado 🔍"))
        except (ValueError, KeyError):
            resultados.append(("error", titulo, dezenas_txt, "Erro na verificação"))

    st.session_state["history_bulk_results"] = resultados

_bulk_results = st.session_state.get("history_bulk_results")
if _bulk_results:
    n_sorteados = sum(1 for r in _bulk_results if r[0] == "success")
    n_ineditos = sum(1 for r in _bulk_results if r[0] == "warning")
    n_erros = sum(1 for r in _bulk_results if r[0] == "error")

    resumo = st.columns(3)
    with resumo[0]:
        st.metric("✅ Já sorteados", n_sorteados)
    with resumo[1]:
        st.metric("🔍 Nunca sorteados", n_ineditos)
    with resumo[2]:
        st.metric("⚠️ Com erro", n_erros)

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    results_per_row = 5
    for i in range(0, len(_bulk_results), results_per_row):
        cols = st.columns(results_per_row)
        for col, (status, titulo, dezenas_txt, msg) in zip(
            cols, _bulk_results[i : i + results_per_row], strict=False
        ):
            with col:
                corpo = f"**{titulo}**\n\n{dezenas_txt}\n\n{msg}"
                if status == "success":
                    st.success(corpo)
                elif status == "warning":
                    st.warning(corpo)
                else:
                    st.error(corpo)

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
            st.session_state.pop("history_bulk_results", None)
            st.success(f"Jogo #{selected_id} removido.")
            st.rerun()
        else:
            st.error("Jogo não encontrado.")

responsible_gaming_footer()
