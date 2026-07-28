import pandas as pd


def export_csv(games, prefix="Bola"):
    """
    Exporta jogos para CSV de forma genérica
    (funciona para Mega-Sena, Lotofácil, etc.)
    """
    if not games:
        raise ValueError("Nenhum jogo para exportar.")

    n_dezenas = len(games[0])

    columns = [f"{prefix}{i}" for i in range(1, n_dezenas + 1)]

    df = pd.DataFrame(games, columns=columns)

    return df.to_csv(index=False).encode("utf-8")
