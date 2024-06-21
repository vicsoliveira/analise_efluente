import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
                change = {
                    'Parâmetro': name,
                    'Data Inicial': first_row['Data'].date(),
                    'Data Final': last_row['Data'].date(),
                    'Valor Inicial': first_row['Valor Obtido'],
                    'Valor Final': last_row['Valor Obtido'],
                    'Mudança (%)': ((last_row['Valor Obtido'] - first_row['Valor Obtido']) / abs(first_row['Valor Obtido'])) * 100
                }
                changes.append(change)

    return pd.DataFrame(changes)

def plot_changes(df):
    if df.empty:
        st.write("No valid data to plot.")
        return

    df = df.sort_values(by='Mudança (%)', key=abs, ascending=False).head(10)  # Take top 10 changes
    parameters = df['Parâmetro']
