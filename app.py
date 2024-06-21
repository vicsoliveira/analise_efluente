import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def process_efluente_data(df):
    records = []
    current_date = None
    current_sample_type = None

    for i, row in df.iterrows():
        # Capture the date from the 'Coleta' row
        if pd.notna(row[1]) and row[1] == 'Coleta':
            current_date = row[2]

        # Capture the sample type from the 'Amostra' row
        if pd.notna(row[1]) and row[1] == 'Amostra':
            current_sample_type = row[2]

        # Skip the header row of parameters
        if row[1] == 'Parâmetro':
            continue

        # Process the parameter rows
        if pd.notna(row[1]) and pd.notna(current_date) and pd.notna(current_sample_type) and row[1] not in ['Elaboração do Laudo', 'NBR', 'Amostra', 'Parâmetro', 'Coleta', 'Parâmetro extra']:
            record = {
                'Data': current_date,
                'Tipo de Amostra': current_sample_type,
                'Parâmetro': row[1],
                'Valor Obtido': row[2],
                'Unidade': row[3],
                'Valor Mínimo (NBR)': row[4],
                'Valor Máximo (NBR)': row[5],
                'Resultado': row[6]
            }
            records.append(record)

    return pd.DataFrame(records)

def calculate_changes(df):
    # Exclude "Efluente Bruto" records
    df = df[df['Tipo de Amostra'] != 'Efluente Bruto']
    
    df['Data'] = pd.to_datetime(df['Data'])
    df['Valor Obtido'] = pd.to_numeric(df['Valor Obtido'], errors='coerce')
    grouped = df.groupby('Parâmetro')

    changes = []

    for name, group in grouped:
        group = group.sort_values(by='Data')
        if len(group) > 1:
            first_row = group.iloc[0]
            last_row = group.iloc[-1]
            if pd.notna(first_row['Valor Obtido']) and pd.notna(last_row['Valor Obtido']):
                percent_change = ((last_row['Valor Obtido'] - first_row['Valor Obtido']) / abs(first_row['Valor Obtido'])) * 100
                if percent_change != 0:
                    change = {
                        'Parâmetro': name,
                        'Data Inicial': first_row['Data'].date(),
                        'Data Final': last_row['Data'].date(),
                        'Valor Inicial': first_row['Valor Obtido'],
                        'Valor Final': last_row['Valor Obtido'],
                        'Mudança (%)': percent_change
                    }
                    changes.append(change)

    return pd.DataFrame(changes)

def plot_changes(df):
    if df.empty:
        st.write("No valid data to plot.")
        return

    df = df.sort_values(by='Mudança (%)', key=abs, ascending=False).head(10)  # Take top 10 changes
    parameters = df['Parâmetro']
    percentages = df['Mudança (%)']
    valores_iniciais = df['Valor Inicial']
    valores_finais = df['Valor Final']

    # Generate a colormap
    cmap = plt.get_cmap('tab20')
    colors = [cmap(i) for i in np.linspace(0, 1, len(parameters))]

    fig, ax = plt.subplots(figsize=(14, 7))
    bars = ax.bar(parameters, percentages, color=colors, edgecolor='black')

    for bar, inicial, final in zip(bars, valores_iniciais, valores_finais):
        height = bar.get_height()
        ax.annotate(f'Inicial: {inicial:.2f}\nFinal: {final:.2f}', 
                    xy=(bar.get_x() + bar.get_width() / 2, height), 
                    xytext=(0, 10),  # 10 points vertical offset
                    textcoords="offset points", 
                    ha='center', va='bottom', fontsize=12, color='white', fontweight='bold', bbox=dict(facecolor='black', alpha=0.7))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, ha='right', fontsize=14, fontweight='bold')
    plt.yticks(fontsize=14, fontweight='bold')
    plt.ylabel('Mudança (%)', fontsize=16, fontweight='bold')
    plt.title('Top 10 Mudanças nos Parâmetros (%)', fontsize=18, fontweight='bold')
    plt.grid(axis='y', linestyle='--', linewidth=0.7)
    plt.tight_layout()
    st.pyplot(fig)

st.title("Efluente Data Processor")

uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=None)
    processed_df = process_efluente_data(df)
    
    st.write("Dados Processados:")
    st.dataframe(processed_df)

    changes_df = calculate_changes(processed_df)

    st.write("Top Mudanças nos Parâmetros:")
    plot_changes(changes_df)

    # Provide download option for the processed data
    st.download_button(
        label="Baixar Dados Processados",
        data=processed_df.to_csv(index=False).encode('utf-8'),
        file_name='dados_processados_efluente.csv',
        mime='text/csv'
    )

    )
