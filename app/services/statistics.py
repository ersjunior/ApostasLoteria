import pandas as pd

def frequency(df, total_bolas: int):
    """
    Calcula a frequência das dezenas para qualquer loteria
    """
    nums = []

    for i in range(1, total_bolas + 1):
        col = f"bola{i}"
        if col in df.columns:
            nums.extend(df[col].tolist())

    return pd.Series(nums).value_counts().sort_index()


def empirical_probability(df, total_bolas: int):
    """
    Calcula a probabilidade empírica das dezenas
    """
    freq = frequency(df, total_bolas)
    total_sorteios = len(df) * total_bolas
    return freq / total_sorteios

def frequency_by_period(df, last_n=50):
    df_slice = df.tail(last_n)

    nums = []
    for i in range(1, 7):
        nums.extend(df_slice[f"bola{i}"].tolist())

    return pd.Series(nums).value_counts().sort_index()
