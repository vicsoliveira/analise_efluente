import streamlit as st
import pandas as pd

# Função para ler e organizar os dados
def read_and_organize_data(file):
    df = pd.read_excel(file, header=None)
    st.write("Primeiras linhas do DataFrame após leitura:")
    st.write(df.head(20))

    # Procurar todas as linhas onde os dados realmente começam
    start_rows = df[df.iloc[:, 1].str.contains('Coleta', na=False)].index.tolist()

    data_list = []
    for start_row in start_rows:
        coleta = df.iloc[start_row + 1, 2]
        elaboracao = df.iloc[start_row + 2, 2]
        amostra = df.iloc[start_row + 4, 2]

        # Coletar todos os parâmetros analisados
        parametros_data = df.iloc[start_row + 6:start_row + 20].reset_index(drop=True)
        parametros_data.columns = ["Parâmetro", "Valor obtido", "Unidade", "Valor mínimo", "Valor máximo", "Resultado"]
        
        for _, row in parametros_data.iterrows():
            if pd.notna(row["Parâmetro"]):
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
