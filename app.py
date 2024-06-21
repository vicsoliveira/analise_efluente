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
    try:
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
    except Exception as e:
        st.error(f"Error calculating changes: {e}")
        return pd.DataFrame()

def compare_efluente_bruto_tratado(df):
    try:
        df['Data'] = pd.to_datetime(df['Data'])
        df['Valor Obtido'] = pd.to_numeric(df['Valor Obtido'], errors='coerce')
        
        comparison = []
        grouped = df.groupby('Data')

        for date, group in grouped:
            bruto = group[group['Tipo de Amostra'] == 'Efluente Bruto']
            tratado = group[group['Tipo de Amostra'] != 'Efluente Bruto']
            if not bruto.empty and not tratado.empty:
                for param in bruto['Parâmetro'].unique():
                    bruto_value = bruto[bruto['Parâmetro'] == param]['Valor Obtido'].values
                    tratado_value = tratado[tratado['Parâmetro'] == param]['Valor Obtido'].values
                    if bruto_value.size > 0 and tratado_value.size > 0:
                        comparison.append({
                            'Data': date,
                            'Parâmetro': param,
                            'Valor Bruto': bruto_value[0],
                            'Valor Tratado': tratado_value[0],
                            'Diferença': bruto_value[0] - tratado_value[0]
                        })

        return pd.DataFrame(comparison)
    except Exception as e:
        st.error(f"Error comparing effluente bruto and tratado: {e}")
        return pd.DataFrame()

def plot_changes(df):
    try:
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
    except Exception as e:
        st.error(f"Error plotting changes: {e}")

def plot_comparison(df):
    try:
        if df.empty:
            st.write("No valid data to plot.")
            return

        df = df.sort_values(by='Diferença', key=abs, ascending=False).head(10)  # Take top 10 differences
        parameters = df['Parâmetro']
        bruto_values = df['Valor Bruto']
        tratado_values = df['Valor Tratado']
        differences = df['Diferença']

        fig, ax = plt.subplots(figsize=(14, 7))
        bar_width = 0.35
        index = np.arange(len(parameters))

        bar1 = ax.bar(index, bruto_values, bar_width, label='Valor Bruto', color='skyblue', edgecolor='black')
        bar2 = ax.bar(index + bar_width, tratado_values, bar_width, label='Valor Tratado', color='lightgreen', edgecolor='black')

        for i, (bruto, tratado) in enumerate(zip(bruto_values, tratado_values)):
            ax.annotate(f'{bruto:.2f}', xy=(i, bruto), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.annotate(f'{tratado:.2f}', xy=(i + bar_width, tratado), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_xlabel('Parâmetros', fontsize=14, fontweight='bold')
        ax.set_ylabel('Valores Obtidos', fontsize=14, fontweight='bold')
        ax.set_title('Comparação de Valores Brutos e Tratados para a Mesma Data', fontsize=16, fontweight='bold')
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(parameters, rotation=45, ha='right', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', linestyle='--', linewidth=0.7)
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting comparison: {e}")

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

    comparison_df = compare_efluente_bruto_tratado(processed_df)

    st.write("Comparação de Valores Brutos e Tratados:")
    plot_comparison(comparison_df)

    # Provide download option for the processed data
    st.download_button(
        label="Baixar Dados")
