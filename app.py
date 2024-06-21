import streamlit as st
import pandas as pd

# Função para ler e organizar os dados
def read_and_organize_data(file):
    df = pd.read_excel(file, header=None)
    st.write("Primeiras linhas do DataFrame após leitura:")
    st.write(df.head(20))

    # Identificar as seções de dados
    coleta_indices = df[df.iloc[:, 1].str.contains('Coleta', na=False)].index

    data_list = []
    for index in coleta_indices:
        coleta_data = df.iloc[index:index+10, :].reset_index(drop=True)
        coleta = coleta_data.iloc[1, 2]
        elaboracao = coleta_data.iloc[2, 2]
        amostra = coleta_data.iloc[4, 2]
        
        parametros_data = df.iloc[index+10:index+20, 1:7].reset_index(drop=True)
        parametros_data.columns = ["Parâmetro", "Valor obtido", "Unidade", "Valor mínimo", "Valor máximo", "Resultado"]

        for _, row in parametros_data.iterrows():
            data_list.append({
                "Coleta": coleta,
                "Elaboração do Laudo": elaboracao,
                "Amostra": amostra,
                "Parâmetro": row["Parâmetro"],
                "Valor obtido": row["Valor obtido"],
                "Unidade": row["Unidade"],
                "Valor mínimo": row["Valor mínimo"],
                "Valor máximo": row["Valor máximo"],
                "Resultado": row["Resultado"]
            })
    
    df_final = pd.DataFrame(data_list)
    
    st.write("DataFrame organizado:")
    st.write(df_final)
    
    return df_final

# Função principal para executar as análises e gerar o arquivo para download
def main():
    st.title("Análise de Efluentes de Estação de Tratamento")
    
    uploaded_file = st.file_uploader("Faça o upload do arquivo Excel com os dados dos efluentes", type=["xlsx"])
    
    if uploaded_file is not None:
        df = read_and_organize_data(uploaded_file)
        
        if df is not None:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar Dados Organizados",
                data=csv,
                file_name='dados_organizados.csv',
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
