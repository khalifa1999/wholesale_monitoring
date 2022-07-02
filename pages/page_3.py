import streamlit as st
import pandas as pd
import plotly_express as px
import io, base64
from main_app import kimiwa


st.title('Wholesale Monitoring app 📈')

st.image('sonatel.jpg', caption='Developed by Khalifa Mamadou NIAMADIO')

# uploaded_file = st.sidebar.file_uploader('Choose a XLSX file', type=['xlsx', 'xlsb'])

uploaded_file = kimiwa()

@st.cache(suppress_st_warning=True)
def to_excel(df):
    # Program implementation for downloading into excel
    towrite = io.BytesIO()
    df.to_excel(towrite, encoding='utf-8', index=False,
                header=True)
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="myfilename.xlsx">Download excel file</a>'
    st.markdown(linko, unsafe_allow_html=True)


@st.experimental_memo
def corridors():
    df = pd.read_excel(uploaded_file, sheet_name='croisé', engine='openpyxl')
    return df


if uploaded_file is not None:
    df = corridors()
    st.write(df)
    # We will merge income and charge dataframes
    revenu = df.groupby(['Operateurs'])['Revenu'].sum()
    charge = df.groupby(['Operateurs'])['Charge'].sum()
    # Sorting of operators
    select_treemap = len(df['Operateurs'].unique().tolist())
    operators_slidetime = st.sidebar.slider(
        'Slide to get corridors by profit from the bigger to the smaller on the matrix',
        1, select_treemap, 8
    )

    ratio = pd.merge(left=revenu,
                     right=charge,
                     left_on='Operateurs',
                     right_on='Operateurs').nlargest(operators_slidetime, 'Revenu')

    matrix = px.scatter_matrix(ratio,
                               dimensions=['Charge', 'Revenu'],
                               color=ratio.index)
    st.plotly_chart(matrix)
    # New dataframe let's drop null values

    difference = pd.merge(left=revenu,
                          right=charge,
                          left_on='Operateurs',
                          right_on='Operateurs')
    difference['difference'] = difference['Revenu'] - difference['Charge']
    difference['difference'] = difference['difference'].astype(float)


    def color_survived(val):
        color = 'black'
        if val < 0:
            color = 'red'
        elif val > 0:
            color = 'green'

        return f'background-color: {color}'


    dataframe = df[['SOP', 'Revenu SOP']].dropna()

    # st.dataframe(dataframe)
    fig = px.scatter(dataframe,
                     x="Revenu SOP",
                     y="SOP"
                     ,size=dataframe['Revenu SOP'],
                     color=dataframe['Revenu SOP'])
    st.plotly_chart(fig)

    operators_bar = st.slider(
        'Slide to the balance on profit and charges of corridors from bigger to smaller',
        1, select_treemap, 9
    )

    sort_diff = difference.nlargest(operators_bar, 'difference')
    # sort_diff['Excedent'] = sort_diff.style.applymap(color_survived, )
    sort_diff['index'] = sort_diff.index
    converted_df = sort_diff.style.applymap(color_survived, subset=['difference'])

    st.dataframe(converted_df)
    to_excel(converted_df)
