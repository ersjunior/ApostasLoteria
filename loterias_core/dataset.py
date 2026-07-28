import os
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from loterias_core.schema import DatasetSchemaError, validate_dataset_schema


# =========================
# NORMALIZAÇÃO
# =========================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "").str.replace("_", "")
    return df


# =========================
# ENRIQUECIMENTO
# =========================
def enrich_dataset(
    df: pd.DataFrame, total_bolas: int, extra_fields: dict | None = None
) -> pd.DataFrame:

    dezenas = [f"bola{i}" for i in range(1, total_bolas + 1)]

    if not all(col in df.columns for col in dezenas):
        raise ValueError(
            f"Colunas inválidas no XLSX.\nEsperado: {dezenas}\nEncontrado: {df.columns.tolist()}"
        )

    def parse_int(v):
        if v is None:
            return None
        v = str(v).strip()
        if not v.isdigit():
            return None
        return int(v)

    df["jogo"] = df[dezenas].apply(
        lambda row: sorted(parse_int(v) for v in row.tolist() if parse_int(v) is not None), axis=1
    )

    df = df[df["jogo"].apply(lambda x: len(x) == total_bolas)]

    # 🔹 CAMPOS EXTRAS
    if extra_fields:
        for field, qtd in extra_fields.items():
            # Campo único (Timemania)
            if qtd == 1 and field in df.columns:
                df[field] = df[field].astype(str).str.strip()
                continue

            cols = [f"{field}{i}" for i in range(1, qtd + 1)]

            if not all(col in df.columns for col in cols):
                raise ValueError(f"Colunas extras inválidas para '{field}': {cols}")

            df[field] = df[cols].apply(
                lambda x: sorted(int(v) for v in x.tolist() if v is not None and str(v).isdigit()),
                axis=1,
            )

    # ✅ RETORNO GARANTIDO EM TODOS OS CASOS
    return df


# =========================
# LOTOMANIA
# =========================
def handle_lotomania(file_path: str) -> pd.DataFrame:
    try:
        # 🔒 Força leitura como TEXTO, sem inferência de tipo
        df_raw = pd.read_excel(file_path, engine="openpyxl", dtype=str, converters=lambda x: str)
    except Exception as e:
        raise ValueError(
            "O arquivo da Lotomania não é um XLSX válido.\n\n"
            "➡️ Baixe novamente no site da Caixa\n"
            "➡️ Não renomeie HTML para .xlsx\n\n"
            f"Erro técnico: {str(e)}"
        ) from e

    df_raw = normalize_columns(df_raw)

    # 🔎 Detectar colunas bola*
    dezenas_cols = [c for c in df_raw.columns if c.startswith("bola")]

    if len(dezenas_cols) < 50:
        raise ValueError(
            f"Não foi possível identificar as 50 dezenas da Lotomania.\n"
            f"Colunas encontradas: {dezenas_cols}"
        )

    jogos = []

    for _, row in df_raw.iterrows():
        dezenas = []

        for col in dezenas_cols:
            val = str(row[col]).strip()

            # Ignorar lixo do XLSX da Caixa
            if val in ("", "-", "nan", "None"):
                continue

            # Aceitar apenas números
            if val.isdigit():
                dezenas.append(int(val))

        if len(dezenas) == 50:
            jogos.append(sorted(dezenas))

    if not jogos:
        raise ValueError(
            "Nenhum jogo válido encontrado na base da Lotomania.\n"
            "O arquivo pode estar corrompido ou em formato inesperado."
        )

    return pd.DataFrame({"jogo": jogos})


# =========================
# SUPER SETE
# =========================
def handle_supersete(file_path: str) -> pd.DataFrame:
    df_raw = pd.read_excel(file_path, dtype=str)
    df_raw = normalize_columns(df_raw)

    colunas = [f"coluna{i}" for i in range(1, 8)]

    if not all(col in df_raw.columns for col in colunas):
        raise ValueError(f"Colunas inválidas do Super Sete. Esperado: {colunas}")

    jogos = []

    for _, row in df_raw.iterrows():
        dezenas = []

        for col in colunas:
            val = str(row[col]).strip()

            if val.isdigit():
                dezenas.append(int(val))

        if len(dezenas) == 7:
            jogos.append(dezenas)

    if not jogos:
        raise ValueError("Nenhum jogo válido encontrado no Super Sete.")

    return pd.DataFrame({"jogo": jogos})


# =========================
# +MILIONÁRIA
# =========================
def handle_mais_milionaria(file_path: str) -> pd.DataFrame:
    df_raw = pd.read_excel(file_path, dtype=str)
    df_raw = normalize_columns(df_raw)

    dezenas_cols = [f"bola{i}" for i in range(1, 7)]
    trevos_cols = ["trevo1", "trevo2"]

    if not all(col in df_raw.columns for col in dezenas_cols):
        raise ValueError(f"Colunas de dezenas inválidas. Esperado: {dezenas_cols}")

    if not all(col in df_raw.columns for col in trevos_cols):
        raise ValueError(f"Colunas de trevos inválidas. Esperado: {trevos_cols}")

    jogos = []

    for _, row in df_raw.iterrows():
        dezenas = []
        trevos = []

        for col in dezenas_cols:
            v = str(row[col]).strip()
            if v.isdigit():
                dezenas.append(int(v))

        for col in trevos_cols:
            v = str(row[col]).strip()
            if v.isdigit():
                trevos.append(int(v))

        if len(dezenas) == 6 and len(trevos) == 2:
            jogos.append({"jogo": sorted(dezenas), "trevos": sorted(trevos)})

    if not jogos:
        raise ValueError("Nenhum jogo válido encontrado na +Milionária.")

    return pd.DataFrame(jogos)


# =========================
# LOADER
# =========================
def load_dataset(
    file_path: str,
    total_bolas: int,
    extra_fields: dict | None = None,
    multiple_draws: bool = False,
    special_handler: str | None = None,
) -> pd.DataFrame:

    if not Path(file_path).exists():
        raise FileNotFoundError(f"Dataset não encontrado: {file_path}")

    # =========================
    # CASOS ESPECIAIS
    # =========================
    if special_handler == "lotomania":
        return handle_lotomania(file_path)

    if special_handler == "supersete":
        return handle_supersete(file_path)

    if special_handler == "mais_milionaria":
        return handle_mais_milionaria(file_path)

    # ⛔ A PARTIR DAQUI LOTOMANIA NÃO PASSA
    df_raw = pd.read_excel(file_path, dtype=str)
    df_raw = normalize_columns(df_raw)

    # =========================
    # LEITURA PADRÃO (SEGURA)
    # =========================
    df_raw = pd.read_excel(file_path, dtype=str)
    df_raw = normalize_columns(df_raw)

    # =========================
    # CASO ESPECIAL: DUPLA SENA
    # =========================
    if multiple_draws:
        all_rows = []

        for draw in [1, 2]:
            dezenas_cols = [f"bola{i}sorteio{draw}" for i in range(1, total_bolas + 1)]

            if not all(col in df_raw.columns for col in dezenas_cols):
                raise ValueError(f"Colunas do sorteio {draw} não encontradas: {dezenas_cols}")

            temp = df_raw[dezenas_cols].copy()
            temp.columns = [f"bola{i}" for i in range(1, total_bolas + 1)]

            temp["jogo"] = temp.apply(
                lambda x: sorted(
                    int(v) for v in x.tolist() if v is not None and v != "-" and v != ""
                ),
                axis=1,
            )

            if "concurso" in df_raw.columns:
                temp["concurso"] = df_raw["concurso"].values
            temp["draw_index"] = draw
            all_rows.append(
                temp[
                    ["jogo"] + (["concurso"] if "concurso" in temp.columns else []) + ["draw_index"]
                ]
            )

        return pd.concat(all_rows, ignore_index=True)

    # =========================
    # RETORNO FINAL DO DF
    # =========================
    return enrich_dataset(df_raw, total_bolas, extra_fields)


# =========================
# ESCRITA ATÔMICA
# =========================
def atomic_write_excel(df: pd.DataFrame, file_path: str) -> None:
    """Grava XLSX em arquivo temporário e renomeia atomicamente."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(suffix=".xlsx", dir=path.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)

    try:
        df.to_excel(tmp_path, index=False, engine="openpyxl")
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def _config_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_bolas": config["total_bolas"],
        "extra_fields": config.get("extra_fields"),
        "multiple_draws": config.get("multiple_draws", False),
        "special_handler": config.get("special_handler"),
    }


def process_raw_dataset(df_raw: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Normaliza, valida schema e enriquece um DataFrame bruto (upload ou download)."""
    df = normalize_columns(df_raw.copy())
    validate_dataset_schema(df, config)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "staging.xlsx"
        df.to_excel(tmp_path, index=False, engine="openpyxl")
        return load_dataset(str(tmp_path), **_config_kwargs(config))


def persist_dataset(
    df_raw: pd.DataFrame,
    config: dict[str, Any],
    *,
    lottery_name: str | None = None,
) -> pd.DataFrame:
    """
    Valida schema, processa e persiste no SQLite.
    Não altera o banco se qualquer etapa falhar.
    """
    from loterias_core.repository import persist_lottery_dataframe

    name = lottery_name or config.get("name", "Loteria")
    lottery_key = config["key"]

    try:
        processed = process_raw_dataset(df_raw, config)
    except DatasetSchemaError:
        raise
    except Exception as exc:
        raise DatasetSchemaError(
            f"Erro ao processar o arquivo de **{name}**.\n\n"
            f"{exc}\n\n"
            "Verifique se o XLSX é o arquivo oficial da modalidade selecionada."
        ) from exc

    try:
        persist_lottery_dataframe(lottery_key, processed, incremental=False)
    except Exception as exc:
        raise DatasetSchemaError(
            f"Falha ao gravar a base de **{name}**.\n\n{exc}\n\nO dataset anterior foi preservado."
        ) from exc

    return processed


def load_dataset_by_key(lottery_key: str) -> pd.DataFrame:
    """Carrega dataset processado do SQLite."""
    from loterias_core.repository import load_lottery_dataframe

    return load_lottery_dataframe(lottery_key)


# =========================
# SALVAR DATASET
# =========================
def save_dataset(df: pd.DataFrame, file_path: str, total_bolas: int):
    df = normalize_columns(df)
    df = enrich_dataset(df, total_bolas)

    atomic_write_excel(df, file_path)
