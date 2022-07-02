import streamlit as st
import os
import pandas as pd
from main_app import kimiwa

uploaded_file = kimiwa()


@st.experimental_memo
def corridors():
    df = pd.read_excel(uploaded_file, sheet_name='croisé', engine='openpyxl')
    return df


if uploaded_file is not None:
    corridors = corridors()
    st.write(corridors)
