import streamlit as st  # pip install streamlit
import pandas as pd  # pip install pandas
import plotly.express as px  # pip install plotly-express
import base64  # Standard Python Module
from io import StringIO, BytesIO  # Standard Python Module
from PIL import Image


def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)


def generate_html_download_link(fig):
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)


st.set_page_config(page_title='Sonatel Wholesale Trend Analyser')
st.title('Wholesale Monitoring app 📈')
st.subheader('Feed me with your Excel file')
st.image('sonatel.jpg', caption='Developed by Khalifa Mamadou NIAMADIO')
uploaded_file = st.sidebar.file_uploader('Choose a XLSX file', type=['xlsx', 'xlsb'])

# Variables globales

Entrant = {'Corridors': 'Corridors', 'Terminaison': 'Terminaison'}

Sortant = {'BILLING_OPERATOR_N': 'BILLING_OPERATOR_N', 'Période': 'Période',
           'Financier': 'Financier', }
liste = {'Entrant': 'Input_Entrant', 'Sortant': 'Input_Sortant'}


@st.experimental_memo(suppress_st_warning=True)
def ecooking(sheet):
    if sheet == 'Input_Entrant':
        df = pd.read_excel(uploaded_file, sheet_name=sheet, engine='openpyxl')
        return df
    elif sheet == 'Input_Sortant':
        df = pd.read_excel(uploaded_file, sheet_name=sheet, engine='openpyxl')
        df['Devise'] = df['Devise'].apply(str)
        return df


if uploaded_file:
    st.markdown('---')
    # sidebar list for differents columns
    # Only got two for the moment entrant and sortant
    sheet_selector = st.sidebar.selectbox(
        'What would you like to analyze 💡',
        liste.keys()
    )

    ecooking(sheet_selector)
    if sheet_selector == 'Entrant':
        groupby_column = st.selectbox(
            'What would you like to analyse? 🧠',
            Entrant.keys()
        )
        # We will deal with the function for input sortant later
        original = ecooking('Input_Entrant')
        top = ecooking('Input_Entrant').groupby([groupby_column], as_index=False)['Financier'].sum()
        set_up = ecooking('Input_Entrant').groupby(['BILLING_OPERATOR'], as_index=False)['Financier'].sum()
        periode = original.groupby(['BILLING_OPERATOR'])['Période'].unique()
        # Markdown on the sidebar for the numbers of {group_column} selected by the user

        # Here we're looking for the number of unique {groupby_column}
        # We first call the function unique on it before putting it into a list
        # We then count the length of that list with len() that we put into biggest variable

        biggest = len(original[groupby_column].unique().tolist())

        # st.write(biggest)
        # Here we create a slider that take the number of unique {groupby_column} represented
        # We then put that slider variable into our largest function so it can automatically update
        # when slider value change

        operators = st.sidebar.slider(
            'Slide to display the desired values based on their size. All the operators are represented 👓', 1, biggest,
            5)
        largest = top.nlargest(operators, "Financier")
        # new set up
        select_treemap = len(original['BILLING_OPERATOR'].unique().tolist())
        operators_slidetime = st.sidebar.slider(
            'Slide to get operators values by revenue in the treemap and the table as well',
            1, select_treemap, 8
        )

        st.write(periode[0][0])
        financier = original.groupby(['BILLING_OPERATOR'])['Financier'].sum()
        slide_time = st.sidebar.slider('Which month revenue do you want to see?', 0, 12, 0)

        if slide_time == 0:
            financier = original.groupby(['BILLING_OPERATOR'])['Financier'].sum()
        elif slide_time == 1:
            financier = original[original['Période'] == '2021-12-01T00:00:00'].groupby(['BILLING_OPERATOR'])[
                'Financier'].sum()
            periode['Période'] = periode[0][0]
        elif slide_time == 2:
            financier = original[original['Période'] == '2022-01-01T00:00:00'].groupby(['BILLING_OPERATOR'])[
                'Financier'].sum()
        elif slide_time == 3:
            financier = original[original['Période'] == '2022-02-01T00:00:00'].groupby(['BILLING_OPERATOR'])[
                'Financier'].sum()

        merge = pd.merge(left=financier, right=periode, left_on='BILLING_OPERATOR',
                         right_on='BILLING_OPERATOR').nlargest(operators_slidetime, 'Financier')
        # setting up the diagrams

        pie = px.pie(largest,
                     names=groupby_column,
                     values='Financier',
                     title=f'<b>Diagramme en camembert des <b>{groupby_column}'
                     )
        area = px.area(merge,
                       x=merge.index,
                       y=merge['Financier'],
                       title='Operators and periode variance based on time ande revenues'
                       )
        # A faire plus tard transformation d'array en date
        # bar = px.bar

        # Displaying the charts
        st.plotly_chart(pie)
        st.plotly_chart(area)
        st.write(merge)



    elif sheet_selector == "Sortant":
        groupby_column = st.selectbox(
            'What would you like to analyse? 🧠',
            Sortant.keys()
        )
        top = ecooking('Input_Sortant')
        # Let's merge these 3 tables to generate a 3D diagram
        x = top.groupby(['BILLING_OPERATOR_N'])['Financier'].sum()
        # y = top.groupby(['Période'])['Financier'].sum()
        z = top.groupby(['BILLING_OPERATOR_N'])['CHARGED_USAGE_D'].sum()

        # Second plot
        char_u = top.groupby(['BILLING_OPERATOR_N'])['CHARGED_USAGE_D'].sum()
        # slider value
        st.write(top['Période'].unique())

        # First plot
        pie = px.pie(top,
                     names=groupby_column,
                     values='Financier',
                     title=f'<b>Diagramme en camembert des <b>{groupby_column}'
                     )
        st.plotly_chart(pie)
        # second plot
        # Here the slider give the user to opportunity to choose the desired number of operators to display
        select_treemap = len(top['BILLING_OPERATOR'].unique().tolist())
        operators_slidetime = st.sidebar.slider(
            'Slide to get operators values by revenue in the treemap and the table as well',
            1, select_treemap, 8
        )

        financier = top.groupby(['BILLING_OPERATOR_N'])['Financier'].sum()
        slide_time = st.sidebar.slider('Which month revenue do you want to see?', 0, 12, 0)

        if slide_time == 0:
            financier = top.groupby(['BILLING_OPERATOR_N'])['Financier'].sum()
        elif slide_time == 1:
            financier = top[top['Période'] == '2021-12-01T00:00:00'].groupby(['BILLING_OPERATOR_N'])['Financier'].sum()
        elif slide_time == 2:
            financier = top[top['Période'] == '2022-01-01T00:00:00'].groupby(['BILLING_OPERATOR_N'])['Financier'].sum()
        elif slide_time == 3:
            financier = top[top['Période'] == '2022-02-01T00:00:00'].groupby(['BILLING_OPERATOR_N'])['Financier'].sum()

        # We merge the fin and char_u dataframes here
        # We use the function nlargest('slider number of selected operators value', 'Column')
        merge = pd.merge(left=financier, right=char_u, left_on='BILLING_OPERATOR_N',
                         right_on='BILLING_OPERATOR_N').nlargest(5, 'Financier')
        merge_table = pd.merge(left=financier, right=char_u, left_on='BILLING_OPERATOR_N',
                               right_on='BILLING_OPERATOR_N').nlargest(operators_slidetime, 'Financier')

        tarte = px.pie(merge,
                       names=merge.index,
                       values='Financier',
                       title='Nos 5 tops opérateurs en termes de CA🤑'
                       )
        # third plot
        scatter_3d = px.scatter_3d(merge_table,
                                   x=merge_table.index,
                                   y=merge_table['CHARGED_USAGE_D'],
                                   z=merge_table['Financier'],
                                   color=merge_table['Financier'],
                                   title='Scatter 3D Operators-Revenue-Charged Usage'
                                   )
        scatter = px.scatter(merge_table,
                             x=merge_table.index,
                             y=merge_table['Financier'],
                             color=merge_table['Financier'],
                             size=merge_table['CHARGED_USAGE_D'],
                             title='Scatter Operators-Revenue-Charged Usage'
                             )
        # Displaying plot
        st.plotly_chart(tarte)
        # st.write(financier)
        st.markdown('La liste de lensemble des opérateurs repertoriés ainsi en que le ca entrant 💰')
        st.write(merge_table)

        st.plotly_chart(scatter_3d)
        st.plotly_chart(scatter)


        # Download function
        list_of_chart = {'camembert': tarte, 'scatter': scatter, 'scatter_3d': scatter_3d}
        download_plot = st.sidebar.selectbox('select the plot you want to download',
                                             list_of_chart.keys())
        generate_html_download_link(list_of_chart.get(download_plot))
        st.balloons()
