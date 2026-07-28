import streamlit as st

from app.core.lotteries import LOTTERIES


def lottery_selector():
    return st.selectbox(
        "🎰 Selecione a Loteria", list(LOTTERIES.keys()), help="Escolha a loteria para análise"
    )
