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

def calculate_percentage_changes(df):
    df['Data'] = pd.to_datetime(df['Data'])
    df['Valor Obtido'] = pd.to_numeric(df['Valor Obtido'], errors='coerce')
    grouped = df.groupby('Parâmetro')

    percentage_changes = {}

    for name, group in grouped:
        group = group.sort_values(by='Data')
        first_value = group['Valor Obtido'].iloc[0]
        last_value = group['Valor Obtido'].iloc[-1]
        if pd.notna(first_value) and pd.notna(last_value) and first_value != 0:
            change = ((last_value - first_value) / abs(first_value)) * 100
            percentage_changes[name] = change

    return percentage_changes

def plot_percentage_changes(changes):
    if not changes:
        st.write("No valid data to plot.")
        return

    changes = dict(sorted(changes.items(), key=lambda item: abs(item[1]), reverse=True)[:10])  # Take top 10 changes
    parameters = list(changes.keys())
    percentages = list(changes.values())

    fig, ax = plt.subplots()
    ax.plot(parameters, percentages, marker='o')

    for i, txt in enumerate(percentages):
        ax.annotate(f'{txt:.2f}%', (parameters[i], percentages[i]), textcoords="offset points", xytext=(0,10), ha='center')

    plt.xticks(rotation=45)
    plt.ylabel('Percentage Change')
    plt.title('Top 10 Parameter Changes (%)')
    plt.grid(True)
    st.pyplot(fig)

st.title("Efluente Data Processor")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=None)
    processed_df = process_efluente_data(df)
    
    st.write("Processed Data:")
    st.dataframe(processed_df)

    percentage_changes = calculate_percentage_changes(processed_df)

    st.write("Top Parameter Changes:")
    plot_percentage_changes(percentage_changes)

    # Provide download option for the processed data
    st.download_button(
        label="Download Processed Data",
        data=processed_df.to_csv(index=False).encode('utf-8'),
        file_name='processed_efluente_data.csv',
        mime='text/csv'
    )
