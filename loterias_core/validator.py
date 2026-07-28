def check_game(dezenas: list[int], df, extra_values: dict | None = None) -> bool:
    """
    Verifica se um jogo já foi sorteado.
    Suporta:
    - dezenas principais
    - campos extras (ex: trevos)
    - datasets heterogêneos da Caixa
    """

    # 🔒 Blindagem absoluta
    if df is None or df.empty or "jogo" not in df.columns:
        return False

    # 🔢 Normalização das dezenas de entrada
    try:
        dezenas = sorted(int(v) for v in dezenas)
    except Exception:
        return False

    # 🔧 Função auxiliar: normalizar qualquer jogo do dataset
    def normalize_game(value):
        if value is None:
            return None

        # Caso já seja lista ou tupla
        if isinstance(value, (list, tuple)):
            try:
                return sorted(int(v) for v in value)
            except Exception:
                return None

        # Caso venha como string "[1, 2, 3]"
        if isinstance(value, str):
            value = value.strip().replace("[", "").replace("]", "")
            parts = [p.strip() for p in value.split(",") if p.strip().isdigit()]
            try:
                return sorted(int(p) for p in parts)
            except Exception:
                return None

        return None

    # =========================
    # CASO COM CAMPOS EXTRAS
    # =========================
    if extra_values:
        # Normalizar extras de entrada
        normalized_extras = {}
        for field, values in extra_values.items():
            try:
                normalized_extras[field] = sorted(int(v) for v in values)
            except Exception:
                return False

        for _, row in df.iterrows():
            jogo_row = normalize_game(row.get("jogo"))

            if jogo_row != dezenas:
                continue

            extras_ok = True
            for field, expected in normalized_extras.items():
                row_value = row.get(field)

                row_extra = normalize_game(row_value)
                if row_extra != expected:
                    extras_ok = False
                    break

            if extras_ok:
                return True

        return False

    # =========================
    # CASO SEM CAMPOS EXTRAS
    # =========================
    for jogo in df["jogo"]:
        jogo_norm = normalize_game(jogo)
        if jogo_norm == dezenas:
            return True

    return False
