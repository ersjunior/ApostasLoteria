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
from app.services.validator import HIT_TIERS, analyze_game, check_game
from app.ui.shell import render_app_chrome
from app.ui.theme import metric_card, page_title, responsible_gaming_footer, section

# Faixas exibidas do maior para o menor (15 → 11).
_TIER_DISPLAY = tuple(sorted(HIT_TIERS, reverse=True))

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
    resultados: list[dict] = []
    datasets: dict[str, object] = {}
    empty_tiers = {tier: 0 for tier in HIT_TIERS}

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
            resultados.append(
                {
                    "status": "error",
                    "titulo": titulo,
                    "dezenas_txt": dezenas_txt,
                    "msg": "Base indisponível",
                    "tier_counts": dict(empty_tiers),
                    "hits_above_11": False,
                }
            )
            continue

        try:
            extras = row.get("extras") or None
            analysis = analyze_game(
                row["dezenas"],
                base,
                extra_values=extras or None,
            )
            if analysis["exact_match"]:
                status, msg = "success", "Já sorteado 🎉"
            else:
                status, msg = "warning", "Nunca sorteado 🔍"
            resultados.append(
                {
                    "status": status,
                    "titulo": titulo,
                    "dezenas_txt": dezenas_txt,
                    "msg": msg,
                    "tier_counts": analysis["tier_counts"],
                    "hits_above_11": analysis["hits_above_11"],
                }
            )
        except (ValueError, KeyError, TypeError):
            resultados.append(
                {
                    "status": "error",
                    "titulo": titulo,
                    "dezenas_txt": dezenas_txt,
                    "msg": "Erro na verificação",
                    "tier_counts": dict(empty_tiers),
                    "hits_above_11": False,
                }
            )

    st.session_state["history_bulk_results"] = resultados

_bulk_results = st.session_state.get("history_bulk_results")
if _bulk_results:
    # Compatibilidade com resultados antigos (tuplas) — força reexecução.
    if _bulk_results and not isinstance(_bulk_results[0], dict):
        st.session_state.pop("history_bulk_results", None)
        st.info("Clique novamente em **Verificar** para atualizar o resumo com as novas métricas.")
    else:
        n_sorteados = sum(1 for r in _bulk_results if r["status"] == "success")
        n_ineditos = sum(1 for r in _bulk_results if r["status"] == "warning")
        n_acima_11 = sum(1 for r in _bulk_results if r.get("hits_above_11"))
        n_erros = sum(1 for r in _bulk_results if r["status"] == "error")
        # Linha 2: quantos jogos do lote tiveram ≥1 acerto na faixa —
        # NÃO soma volumes entre jogos (isso inflava além do nº de sorteios da base).
        jogos_por_faixa = {
            tier: sum(
                1 for r in _bulk_results if (r.get("tier_counts") or {}).get(tier, 0) > 0
            )
            for tier in HIT_TIERS
        }

        linha1 = st.columns(4)
        with linha1[0]:
            metric_card("Já sorteados", str(n_sorteados), "✅")
        with linha1[1]:
            metric_card("Nunca sorteados", str(n_ineditos), "🔍")
        with linha1[2]:
            metric_card("Sorteados com mais de 11 dezenas", str(n_acima_11), "🎯")
        with linha1[3]:
            metric_card("Com erro", str(n_erros), "⚠️")

        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

        linha2 = st.columns(5)
        for col, tier in zip(linha2, _TIER_DISPLAY, strict=True):
            with col:
                metric_card(f"{tier} dezenas", str(jogos_por_faixa[tier]), "🎱")

        st.caption(
            "Linha 2 = **quantos jogos** do lote tiveram ao menos um sorteio com "
            "exatamente N dezenas em comum. "
            "Em cada card, o volume é **por jogo** (quantos sorteios da base bateram "
            "11, 12, 13, 14 ou 15 dezenas com aquela aposta) — nunca soma entre jogos. "
            "**Sorteados com mais de 11** = jogos com ao menos um acerto em 12–15."
        )

        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

        results_per_row = 5
        for i in range(0, len(_bulk_results), results_per_row):
            cols = st.columns(results_per_row)
            for col, item in zip(
                cols, _bulk_results[i : i + results_per_row], strict=False
            ):
                with col:
                    tiers = item.get("tier_counts") or {}
                    # Duas quebras forçam parágrafo no Markdown do Streamlit
                    # (um único \n colapsa e as faixas ficavam lado a lado).
                    tiers_txt = "\n\n".join(
                        f"{tier} dezenas: {tiers.get(tier, 0)}" for tier in _TIER_DISPLAY
                    )
                    corpo = (
                        f"**{item['titulo']}**\n\n"
                        f"{item['dezenas_txt']}\n\n"
                        f"{item['msg']}\n\n"
                        f"{tiers_txt}"
                    )
                    if item["status"] == "success":
                        st.success(corpo)
                    elif item["status"] == "warning":
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
