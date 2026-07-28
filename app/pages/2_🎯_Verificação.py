import sys
from pathlib import Path

import streamlit as st

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.core.lotteries import LOTTERIES
from app.services.dataset import load_dataset
from app.services.validator import check_game
from app.ui.theme import page_title, section
from app.ui.theme_manager import apply_theme, init_theme

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Verificação de Jogos", layout="wide")

init_theme()
apply_theme()


# =========================
# TÍTULO
# =========================
page_title(
    "🎯 Verificação de Jogos", "Confira se seus jogos já foram sorteados em diferentes loterias"
)

# =========================
# SELETOR DE LOTERIA
# =========================
section("🎲 Seleção da Loteria")

lottery_name = st.selectbox("Escolha a loteria", list(LOTTERIES.keys()))

config = LOTTERIES[lottery_name]

st.markdown(
    f"""
    <div style="
        margin-top:10px;
        padding:10px 15px;
        border-left:5px solid {config["color"]};
        background-color: rgba(255,255,255,0.02);
        border-radius:6px;
    ">
        <strong>{config["icon"]} {lottery_name}</strong><br>
        Insira jogos com <b>{config["total_bolas"]} dezenas</b>.
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
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    st.error(f"⚠️ Erro ao carregar a base da **{lottery_name}**\n\n{str(e)}")
    st.write("DEBUG special_handler:", config.get("special_handler"))
    st.stop()

# =========================
# DEBUG — VALIDAÇÃO DO DATASET
# =========================
# st.subheader("🧪 Debug do Dataset (temporário)")
#
# st.write(type(df))
# st.write(df.head())
# st.write("Total de jogos:", len(df))
#
# st.write("Total de jogos carregados:", len(df))
# st.write("Colunas do DataFrame:", df.columns.tolist())
#
## Mostrar alguns jogos reais
# st.write("Exemplo de jogos reais do dataset:")
# st.write(df["jogo"].head(10))
#
## Teste manual de um jogo específico
# test_game = [6, 29, 33, 38, 53, 56]
# test_game = sorted(test_game)
#
# matches = df[df["jogo"].apply(lambda x: x == test_game)]
#
# st.write("Teste manual do jogo:", test_game)
# st.write("Ocorrências encontradas:", len(matches))


# =========================
# INSERÇÃO DOS JOGOS
# =========================
section("📝 Inserção dos Jogos")

TOTAL_GAMES = 3
COLS_PER_ROW = 3

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

games = []
game_index = 0

for _ in range(TOTAL_GAMES // COLS_PER_ROW):
    cols = st.columns(COLS_PER_ROW)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    for col in cols:
        if game_index >= TOTAL_GAMES:
            continue

        jogo_numero = game_index + 1

        # =========================
        # DEZENAS PRINCIPAIS
        # =========================
        dezenas_input = col.text_input(
            f"{config['icon']} Jogo {jogo_numero}",
            placeholder=config.get(
                "placeholder", f"Informe {config['total_bolas']} dezenas separadas por vírgula"
            ),
            key=f"{config['key']}_game_{game_index}",
        )

        extras_inputs = {}

        # =========================
        # CAMPOS EXTRAS (TREVO)
        # =========================
        if "extra_fields" in config:
            for field, qtd in config["extra_fields"].items():
                extra = col.text_input(
                    f"{config['icon']} {field.capitalize()} ({qtd})",
                    placeholder=f"{qtd} números separados por vírgula",
                    key=f"{config['key']}_{field}_{game_index}",
                )

                if extra:
                    extras_inputs[field] = [int(x.strip()) for x in extra.split(",")]

        # =========================
        # SALVAR JOGO
        # =========================
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

if st.button(f"{config['icon']} Verificar Jogos"):
    section("📋 Resultados")

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    RESULTS_PER_ROW = 5
    results = []

    # =========================
    # PROCESSAR JOGOS
    # =========================
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

        except ValueError:
            results.append(("error", f"{config['icon']} Jogo {idx}", "Formato inválido"))

    # =========================
    # RENDERIZAÇÃO EM GRID
    # =========================
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
