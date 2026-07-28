import streamlit as st

from app.services.dataset import load_dataset


@st.cache_data(ttl=3600)
def load_dataset_cached(lottery_key: str = "megasena"):
    return load_dataset(lottery_key=lottery_key)
