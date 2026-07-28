import random


def generate_unique_combinations(
    df,
    n_games: int = 12,
    total_bolas: int = 6,
    extra_fields: dict | None = None,
    universo: int | None = None,
):
    """
    Gera combinações inéditas que nunca foram sorteadas.

    Usa amostragem aleatória uniforme — não há modelo preditivo.
    """

    if universo is None:
        raise ValueError("Universo não informado para geração dos jogos.")

    existing_games = set(tuple(sorted(jogo)) for jogo in df["jogo"] if isinstance(jogo, list))

    generated = []
    attempts = 0
    max_attempts = n_games * 500

    while len(generated) < n_games and attempts < max_attempts:
        attempts += 1

        dezenas = sorted(random.sample(range(1, universo + 1), total_bolas))

        if tuple(dezenas) in existing_games:
            continue

        game = dezenas.copy()

        # =========================
        # CAMPOS EXTRAS (ex: trevos)
        # =========================
        extras = {}
        if extra_fields:
            for field, qtd in extra_fields.items():
                # ignorar metacampos como trevos_universo
                if not field.endswith("_universo"):
                    universo_extra = extra_fields.get(f"{field}_universo", None)
                    if universo_extra:
                        extras[field] = sorted(random.sample(range(1, universo_extra + 1), qtd))

        generated.append({"dezenas": game, "extras": extras if extras else None})

    return generated
