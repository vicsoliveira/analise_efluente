import streamlit as st
import pandas as pd

# Função para carregar e processar o arquivo Excel
def process_excel(file):
    df = pd.read_excel(file, sheet_name=None)
    return df

# Configuração do Streamlit
st.title('Análise de Amostras de Efluente')

uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")

if uploaded_file is not None:
    # Processa o arquivo Excel
    data = process_excel(uploaded_file)

    # Exibe os nomes das planilhas
    sheet_names = list(data.keys())
    st.write("Planilhas encontradas:", sheet_names)

    # Loop para exibir cada planilha
    for sheet_name in sheet_names:
        st.subheader(f'Planilha: {sheet_name}')
        df = data[sheet_name]
        st.write(df)

        # Verifica se a planilha contém os parâmetros da NBR 16783
        if 'Parâmetro' in df.columns and 'Resultado' in df.columns and 'Padrão NBR 16783' in df.columns:
            df['Conformidade'] = df.apply(lambda row: 'Conforme' if row['Resultado'] <= row['Padrão NBR 16783'] else 'Não Conforme', axis=1)
            st.write(df)
        else:
            st.write("Esta planilha não contém os parâmetros necessários para comparação com a NBR 16783.")

