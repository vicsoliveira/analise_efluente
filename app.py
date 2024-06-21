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

    # Dados organizados
    df_nbr = pd.DataFrame()
    df_no_nbr = pd.DataFrame()

    # Loop para processar e organizar cada planilha
    for sheet_name in sheet_names:
        st.subheader(f'Planilha: {sheet_name}')
        df = data[sheet_name]

        # Verifica e organiza os dados conforme solicitado
        if 'Parâmetro' in df.columns and 'Resultado' in df.columns:
            if 'Padrão NBR 16783' in df.columns:
                df['Conformidade'] = df.apply(lambda row: 'Conforme' if row['Resultado'] <= row['Padrão NBR 16783'] else 'Não Conforme', axis=1)
                df_nbr = pd.concat([df_nbr, df])
            else:
                df_no_nbr = pd.concat([df_no_nbr, df])

        st.write(df)

    # Exibe os dados organizados
    st.subheader('Parâmetros com comparação NBR 16783')
    st.write(df_nbr)

    st.subheader('Parâmetros sem comparação NBR 16783')
    st.write(df_no_nbr)

    # Salva os dados organizados em arquivos separados (opcional)
    df_nbr.to_excel('/mnt/data/Parametros_com_NBR.xlsx', index=False)
    df_no_nbr.to_excel('/mnt/data/Parametros_sem_NBR.xlsx', index=False)

    st.success('Dados organizados e salvos com sucesso!')
    st.markdown(f"[Download Parâmetros com NBR](mnt/data/Parametros_com_NBR.xlsx)")
    st.markdown(f"[Download Parâmetros sem NBR](mnt/data/Parametros_sem_NBR.xlsx)")
