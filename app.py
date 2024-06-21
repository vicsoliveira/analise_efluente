import streamlit as st
import pandas as pd

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
        if pd.notna(row[1]) and pd.notna(current_date) and pd.notna(current_sample_type) and row[1] not in ['Elaboração do Laudo', 'NBR', 'Amostra', 'Parâmetro', 'Coleta']:
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

st.title("Efluente Data Processor")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=None)
    st.write("Uploaded Data:")
    st.dataframe(df)

    processed_df = process_efluente_data(df)
    st.write("Processed Data:")
    st.dataframe(processed_df)

    # Provide download option for the processed data
    st.download_button(
        label="Download Processed Data",
        data=processed_df.to_csv(index=False).encode('utf-8'),
        file_name='processed_efluente_data.csv',
        mime='text/csv'
    )
