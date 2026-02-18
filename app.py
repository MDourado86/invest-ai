import streamlit as st
import pandas as pd

st.title("Sugestões de Investimento Diárias")

try:
    df = pd.read_csv('signals.csv')
    st.dataframe(df)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.info("Por favor, rode o update.py para gerar o arquivo signals.csv.")

