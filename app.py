import streamlit as st
import pandas as pd
from io import BytesIO

# Função para carregar e processar o arquivo Excel
def process_excel(file):
    df = pd.read_excel(file, sheet_name=None)
    return df

# Função para criar o botão de download
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

# Configuração do Streamlit
st.title('Análise de Amostras de Efluente')

uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")

if uploaded_file is not None:
    # Processa o arquivo Excel
    data = process_excel(uploaded_file)

    # Exibe os nomes das planilhas
    sheet_names = list(data.keys())
    st.write("Planilhas encontradas:", sheet_names)

    # Dados organizados
    df_nbr = pd.DataFrame()
    df_no_nbr = pd.DataFrame()

    # Loop para processar e organizar cada planilha
    for sheet_name in sheet_names:
        st.subheader(f'Planilha: {sheet_name}')
        df = data[sheet_name]

        # Verifica se a planilha contém os parâmetros da NBR 16783
        if 'Parâmetro' in df.columns and 'Resultado' in df.columns:
            if 'Padrão NBR 16783' in df.columns:
                df['Conformidade'] = df.apply(lambda row: 'Conforme' if row['Resultado'] <= row['Padrão NBR 16783'] else 'Não Conforme', axis=1)
                df_nbr = pd.concat([df_nbr, df])
            else:
                df_no_nbr = pd.concat([df_no_nbr, df])

        st.write(df)

    # Exibe os dados organizados
    if not df_nbr.empty:
        st.subheader('Parâmetros com comparação NBR 16783')
        st.write(df_nbr)

    if not df_no_nbr.empty:
        st.subheader('Parâmetros sem comparação NBR 16783')
        st.write(df_no_nbr)

    # Cria os arquivos para download
    if not df_nbr.empty:
        df_nbr_excel = to_excel(df_nbr)
        st.download_button(
            label="Download Parâmetros com NBR",
            data=df_nbr_excel,
            file_name='Parametros_com_NBR.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    if not df_no_nbr.empty:
        df_no_nbr_excel = to_excel(df_no_nbr)
        st.download_button(
            label="Download Parâmetros sem NBR",
            data=df_no_nbr_excel,
            file_name='Parametros_sem_NBR.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
