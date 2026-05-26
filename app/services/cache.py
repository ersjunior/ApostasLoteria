import streamlit as st
from app.services.dataset import load_dataset

@st.cache_data(ttl=3600)
def load_dataset_cached():
    return load_dataset()
