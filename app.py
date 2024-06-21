import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

# Função para ler e aplicar o arquivo .gitignore
def load_gitignore():
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())
        return spec
    except FileNotFoundError:
        st.warning("Arquivo .gitignore não encontrado. Ignorando.")
        return None

# Função para ler e organizar os dados
def read_and_organize_data(file):
    df = pd.read_excel(file, header=None)
    st.write("Primeiras linhas do DataFrame após leitura:")
    st.write(df.head(20))

    # Procurar todas as linhas onde os dados realmente começam
    start_rows = df[df.iloc[:, 1].str.contains('Coleta', na=False)].index.tolist()

    data_frames = []
    for start_row in start_rows:
        # Identificar a linha onde os dados começam
        coleta = df.iloc[start_row + 1, 2]
        elaboracao = df.iloc[start_row + 2, 2]
        nbr = df.iloc[start_row + 3, 2]
        amostra = df.iloc[start_row + 4, 2]

        # Recarregar os dados a partir da linha correta
        sub_df = df.iloc[start_row + 5:start_row + 15].reset_index(drop=True)
        sub_df.columns = ["Unnamed: 0", "Parâmetro", "Valor obtido", "Unidade", "Valor mínimo", "Valor máximo", "Resultado"]

        # Adicionar colunas 'Coleta', 'Elaboração do Laudo', 'NBR' e 'Amostra' manualmente
        sub_df["Coleta"] = coleta
        sub_df["Elaboração do Laudo"] = elaboracao
        sub_df["NBR"] = nbr
        sub_df["Amostra"] = amostra

        # Verificar o DataFrame após ajustes
        st.write("DataFrame após ajustes:")
        st.write(sub_df.head(10))

        # Tentar converter a coluna 'Coleta' para datetime, tratando possíveis erros
        try:
            sub_df['Coleta'] = pd.to_datetime(sub_df['Coleta'], format='%d/%m/%Y')
        except ValueError:
            try:
                sub_df['Coleta'] = pd.to_datetime(sub_df['Coleta'], format='%Y-%m-%d')
            except ValueError:
                sub_df['Coleta'] = pd.to_datetime(sub_df['Coleta'], errors='coerce')

        # Verificar se há datas não convertidas
        if sub_df['Coleta'].isnull().any():
            st.warning("Algumas datas na coluna 'Coleta' não puderam ser convertidas e foram definidas como NaT.")

        sub_df.sort_values(by='Coleta', inplace=True)
        data_frames.append(sub_df)

    # Concatenar todos os DataFrames processados
    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
    else:
        st.error("Nenhum dado válido encontrado para processamento.")
        return None

    return df

# Função para analisar a evolução temporal dos resultados dos efluentes tratados
def analyze_temporal_evolution(df):
    treated = df[df['Amostra'].str.contains('Tratado', case=False, na=False)]
    parameters = treated['Parâmetro'].unique()

    for parameter in parameters:
        parameter_data = treated[treated['Parâmetro'] == parameter]
        plt.figure(figsize=(10, 6))
        plt.plot(parameter_data['Coleta'], parameter_data['Valor obtido'], label='Valor obtido')
        if not parameter_data['Valor mínimo'].isnull().all():
            plt.plot(parameter_data['Coleta'], parameter_data['Valor mínimo'], label='Valor mínimo', linestyle='--')
        if not parameter_data['Valor máximo'].isnull().all():
            plt.plot(parameter_data['Coleta'], parameter_data['Valor máximo'], label='Valor máximo', linestyle='--')
        plt.xlabel('Data')
        plt.ylabel(f'Valor do {parameter}')
        plt.title(f'Evolução Temporal do {parameter} em Efluentes Tratados')
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

# Função para analisar a qualidade do tratamento
def analyze_treatment_quality(df):
    parameters = df['Parâmetro'].unique()
    quality_analysis = []

    for parameter in parameters:
        raw = df[(df['Amostra'].str.contains('Bruto', case=False, na=False)) & (df['Parâmetro'] == parameter)]
        treated = df[(df['Amostra'].str.contains('Tratado', case=False, na=False)) & (df['Parâmetro'] == parameter)]

        st.write(f"Analisando o parâmetro: {parameter}")
        st.write("Dados de Efluente Bruto:")
        st.write(raw)
        st.write("Dados de Efluente Tratado:")
        st.write(treated)

        if not raw.empty and not treated.empty:
            merged = pd.merge(raw, treated, on=['Coleta', 'Parâmetro'], suffixes=('_Bruto', '_Tratado'))
            if not merged.empty:
                merged['Diferença'] = merged['Valor obtido_Bruto'] - merged['Valor obtido_Tratado']
                quality_analysis.append(merged[['Coleta', 'Amostra_Bruto', 'Parâmetro', 'Valor obtido_Bruto', 'Valor obtido_Tratado', 'Diferença']])
            else:
                st.warning(f"Não há dados combinados para o parâmetro {parameter}")

    if quality_analysis:
        quality_df = pd.concat(quality_analysis)
        return quality_df
    else:
        st.error("Nenhum dado de qualidade de tratamento encontrado.")
        return None

# Função principal para executar as análises e gerar o arquivo para download
def main():
    st.title("Análise de Efluentes de Estação de Tratamento")

    # Carregar e aplicar o arquivo .gitignore
    spec = load_gitignore()
    if spec:
        st.success(".gitignore aplicado com sucesso.")
    else:
        st.info("Nenhum .gitignore aplicado.")

    uploaded_file = st.file_uploader("Faça o upload do arquivo Excel com os dados dos efluentes", type=["xlsx"])

    if uploaded_file is not None:
        df = read_and_organize_data(uploaded_file)
        
        if df is not None:
            st.subheader("Análise Temporal dos Efluentes Tratados")
            analyze_temporal_evolution(df)

            st.subheader("Análise da Qualidade do Tratamento")
            quality_df = analyze_treatment_quality(df)
            if quality_df is not None:
                st.write(quality_df)

                csv = quality_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar Análise da Qualidade do Tratamento",
                    data=csv,
                    file_name='analise_qualidade_tratamento.csv',
                    mime='text/csv',
                )

if __name__ == "__main__":
    main()
