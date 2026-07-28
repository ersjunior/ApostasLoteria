"""Validação de schema de datasets antes da persistência."""

from __future__ import annotations

from typing import Any

import pandas as pd

from loterias_core.lotteries import LOTTERIES_BY_KEY, LotteryConfig


class DatasetSchemaError(ValueError):
    """Erro amigável quando o arquivo não atende ao schema esperado."""


def _as_config(config: LotteryConfig | dict[str, Any]) -> dict[str, Any]:
    if isinstance(config, LotteryConfig):
        return config.to_dict()
    return config


def _required_columns(config: dict[str, Any]) -> list[str]:
    special = config.get("special_handler")
    total = config["total_bolas"]

    if special == "lotomania":
        return []

    if special == "supersete":
        return [f"coluna{i}" for i in range(1, 8)]

    if special == "mais_milionaria":
        return [f"bola{i}" for i in range(1, 7)] + ["trevo1", "trevo2"]

    if config.get("multiple_draws"):
        cols: list[str] = []
        for draw in (1, 2):
            cols.extend(f"bola{i}sorteio{draw}" for i in range(1, total + 1))
        return cols

    cols = [f"bola{i}" for i in range(1, total + 1)]
    extra_fields = config.get("extra_fields") or {}
    for field, qtd in extra_fields.items():
        if qtd == 1:
            cols.append(field)
        else:
            cols.extend(f"{field}{i}" for i in range(1, qtd + 1))
    return cols


def _parse_int(value: Any) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if text in ("", "-", "nan", "None"):
        return None
    if text.isdigit():
        return int(text)
    return None


def _validate_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
    *,
    min_val: int,
    max_val: int,
    lottery_name: str,
) -> None:
    errors: list[str] = []

    for col in columns:
        if col not in df.columns:
            continue

        invalid_samples: list[str] = []
        for idx, raw in df[col].head(200).items():
            parsed = _parse_int(raw)
            if parsed is None:
                if str(raw).strip() not in ("", "-", "nan", "None"):
                    invalid_samples.append(f"linha {idx + 2}: '{raw}'")
            elif parsed < min_val or parsed > max_val:
                invalid_samples.append(f"linha {idx + 2}: {parsed} (esperado {min_val}–{max_val})")

            if len(invalid_samples) >= 3:
                break

        if invalid_samples:
            errors.append(f"  • {col}: {', '.join(invalid_samples)}")

    if errors:
        raise DatasetSchemaError(
            f"Valores inválidos na base da **{lottery_name}**.\n\n"
            + "\n".join(errors)
            + "\n\nVerifique se o arquivo é o XLSX oficial da Caixa para esta modalidade."
        )


def validate_dataset_schema(
    df: pd.DataFrame,
    config: LotteryConfig | dict[str, Any],
    *,
    lottery_name: str | None = None,
) -> None:
    """
    Valida colunas, presença de dados e faixas numéricas antes de persistir.
    Levanta DatasetSchemaError com mensagem clara — nunca exceção crua.
    """
    cfg = _as_config(config)
    name = lottery_name or next(
        (c.name for c in LOTTERIES_BY_KEY.values() if c.to_dict() == cfg),
        "Loteria",
    )

    if df is None or df.empty:
        raise DatasetSchemaError(
            f"O arquivo enviado para **{name}** está vazio.\n\n"
            "Baixe novamente o XLSX oficial no site da Caixa."
        )

    special = cfg.get("special_handler")
    universo = cfg["universo"]

    if special == "lotomania":
        bola_cols = [c for c in df.columns if c.startswith("bola")]
        if len(bola_cols) < 50:
            raise DatasetSchemaError(
                f"Schema inválido para **{name}**.\n\n"
                f"Esperadas pelo menos 50 colunas de dezenas (bola*); "
                f"encontradas {len(bola_cols)}: {bola_cols[:10]}..."
            )
        _validate_numeric_columns(df, bola_cols[:50], min_val=0, max_val=99, lottery_name=name)
        return

    required = _required_columns(cfg)
    missing = [col for col in required if col not in df.columns]

    if missing:
        found = [c for c in df.columns if c.startswith(("bola", "coluna", "trevo"))]
        raise DatasetSchemaError(
            f"Schema inválido para **{name}**.\n\n"
            f"Colunas obrigatórias ausentes: {missing}\n"
            f"Colunas de dezenas encontradas: {found or '(nenhuma)'}\n\n"
            "Confirme se selecionou a modalidade correta e se o arquivo é o XLSX oficial."
        )

    if special == "supersete":
        _validate_numeric_columns(df, required, min_val=0, max_val=9, lottery_name=name)
    elif special == "mais_milionaria":
        dezenas = [f"bola{i}" for i in range(1, 7)]
        trevos = ["trevo1", "trevo2"]
        _validate_numeric_columns(df, dezenas, min_val=1, max_val=50, lottery_name=name)
        _validate_numeric_columns(df, trevos, min_val=1, max_val=6, lottery_name=name)
    elif cfg.get("multiple_draws"):
        draw_cols = [c for c in required if c.startswith("bola")]
        _validate_numeric_columns(df, draw_cols, min_val=1, max_val=universo, lottery_name=name)
    else:
        bola_cols = [c for c in required if c.startswith("bola")]
        _validate_numeric_columns(df, bola_cols, min_val=1, max_val=universo, lottery_name=name)
