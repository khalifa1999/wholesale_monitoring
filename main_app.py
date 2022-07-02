# Contents of ~/my_app/main_page.py
import streamlit as st
import pandas as pd

st.markdown("# Welcome 🎈")
st.title('Wholesale Monitoring app 📈')
st.subheader('Feed me with your Excel file')
st.image('sonatel.jpg', caption='Developed by Khalifa Mamadou NIAMADIO')

uploaded_f = st.sidebar.file_uploader('Choose a XLSX file', type=['xlsx', 'xlsb'])
countdown = 0

if uploaded_f is not None:
    @st.experimental_memo
    def kimiwa():
        uploaded_file = uploaded_f
        return uploaded_file

# os.environ['global'] = uploaded_f
# st.write(uploaded_f)
# os.environ['uo'] = uploaded_f
# st.write(os.environ['global'])
