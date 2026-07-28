import sys
from pathlib import Path

import streamlit as st

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.services.dataset import load_dataset
from app.services.user_history import SOURCE_VERIFY, add_user_games
from app.services.validator import check_game
from app.ui.shell import render_app_chrome
from app.ui.theme import lottery_badge, page_title, responsible_gaming_footer, section

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Verificação de Jogos", layout="wide")

lottery_name, config = render_app_chrome(show_lottery=True)

page_title(
    "🎯 Verificação de Jogos", "Confira se seus jogos já foram sorteados em diferentes loterias"
)
lottery_badge(
    lottery_name,
    config,
    detail=f"Insira jogos com <b>{config['total_bolas']} dezenas</b>.",
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
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    st.error(f"⚠️ Erro ao carregar a base da **{lottery_name}**\n\n{str(e)}")
    st.stop()


# =========================
# INSERÇÃO DOS JOGOS
# =========================
section("📝 Inserção dos Jogos")

COLS_PER_ROW = 3

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

n_games = st.slider(
    "Quantidade de jogos",
    min_value=1,
    max_value=20,
    value=5,
    key="verify_n_games",
)

games = []
game_index = 0

for _row in range((n_games + COLS_PER_ROW - 1) // COLS_PER_ROW):
    cols = st.columns(COLS_PER_ROW)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    for col in cols:
        if game_index >= n_games:
            break

        jogo_numero = game_index + 1

        dezenas_input = col.text_input(
            f"{config['icon']} Jogo {jogo_numero}",
            placeholder=config.get(
                "placeholder", f"Informe {config['total_bolas']} dezenas separadas por vírgula"
            ),
            key=f"{config['key']}_game_{game_index}",
        )

        extras_inputs = {}

        if "extra_fields" in config:
            for field, qtd in config["extra_fields"].items():
                if field.endswith("_universo"):
                    continue
                extra = col.text_input(
                    f"{config['icon']} {field.capitalize()} ({qtd})",
                    placeholder=f"{qtd} números separados por vírgula",
                    key=f"{config['key']}_{field}_{game_index}",
                )

                if extra:
                    extras_inputs[field] = [int(x.strip()) for x in extra.split(",")]

        if dezenas_input:
            games.append(
                {
                    "index": jogo_numero,
                    "dezenas": dezenas_input,
                    "extras": extras_inputs if extras_inputs else None,
                }
            )

        game_index += 1


# =========================
# VERIFICAÇÃO
# =========================
st.markdown("<div style='margin-top:25px'></div>", unsafe_allow_html=True)

_results_key = "verify_last_results"
_valid_key = "verify_last_valid"
_lottery_key_state = "verify_last_lottery_key"

if st.session_state.get(_lottery_key_state) != config["key"]:
    st.session_state.pop(_results_key, None)
    st.session_state.pop(_valid_key, None)
    st.session_state[_lottery_key_state] = config["key"]

if st.button(f"{config['icon']} Verificar Jogos"):
    RESULTS_PER_ROW = 5
    results = []
    valid_games = []

    for game in games:
        idx = game["index"]

        try:
            raw_values = [n.strip() for n in game["dezenas"].split(",")]

            dezenas = []
            for v in raw_values:
                if not v.isdigit():
                    raise ValueError(f"Valor inválido: {v}")
                dezenas.append(int(v))

            dezenas = sorted(dezenas)

            if len(dezenas) != config["total_bolas"]:
                results.append(
                    (
                        "error",
                        f"{config['icon']} Jogo {idx}",
                        f"Informe exatamente {config['total_bolas']} dezenas",
                    )
                )
                continue

            found = check_game(dezenas, df, extra_values=game["extras"])

            if found:
                results.append(("success", f"{config['icon']} Jogo {idx}", "Já foi sorteado 🎉"))
            else:
                results.append(("warning", f"{config['icon']} Jogo {idx}", "Nunca foi sorteado 🔍"))

            valid_games.append({"dezenas": dezenas, "extras": game["extras"]})

        except ValueError:
            results.append(("error", f"{config['icon']} Jogo {idx}", "Formato inválido"))

    st.session_state[_results_key] = results
    st.session_state[_valid_key] = valid_games

results = st.session_state.get(_results_key) or []
valid_games = st.session_state.get(_valid_key) or []

if results:
    section("📋 Resultados")
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    RESULTS_PER_ROW = 5
    for i in range(0, len(results), RESULTS_PER_ROW):
        cols = st.columns(RESULTS_PER_ROW)

        for col, result in zip(cols, results[i : i + RESULTS_PER_ROW], strict=False):
            status, title, message = result

            with col:
                if status == "success":
                    st.success(f"**{title}**\n\n{message}")
                elif status == "warning":
                    st.warning(f"**{title}**\n\n{message}")
                else:
                    st.error(f"**{title}**\n\n{message}")

    if valid_games:
        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        if st.button("💾 Salvar jogos válidos no histórico", key=f"save_verify_{config['key']}"):
            try:
                ids = add_user_games(
                    config["key"],
                    valid_games,
                    source=SOURCE_VERIFY,
                    note=f"Verificação — {lottery_name}",
                )
                st.success(f"{len(ids)} jogo(s) salvos no histórico local.")
            except Exception as exc:
                st.error(f"Não foi possível salvar no histórico.\n\n{exc}")

responsible_gaming_footer()
