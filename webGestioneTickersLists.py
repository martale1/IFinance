import streamlit as st
import os
from dbValidTickers import dbValidTickers
import pandas as pd


def valid_tickers_page():
    # Inizializza la classe dbValidTickers
    db_tickers = dbValidTickers()

    st.title("📈 Importazione e Gestione dei Ticker Validi")

    # Recupera il percorso corrente per la directory dei file
    current_dir = "/home/developer/PycharmProjects/learningProjects/IFinance"

    # Filtra i file nella directory corrente per includere quelli che iniziano con 'validtickers'
    # e terminano con estensione '.xlsx' o '.xls'
    files = [f for f in os.listdir(current_dir) if
             f.lower().startswith('validtickers') and f.lower().endswith(('.xlsx', '.xls'))]

    # Importazione dei file selezionati
    if files:
        st.header("📥 Importazione dei File Ticker")
        st.markdown("Seleziona i file che desideri importare nel database:")

        selected_files = {}
        for file in files:
            selected_files[file] = st.checkbox(f"Seleziona {file}", value=False)

        files_to_import = [file for file, selected in selected_files.items() if selected]

        if st.button("Importa File Selezionati"):
            if files_to_import:
                for file in files_to_import:
                    file_path = os.path.join(current_dir, file)
                    db_tickers.import_from_file(file_path)
                    st.success(f"File '{file}' importato con successo.")
                st.experimental_rerun()  # Ricarica la pagina per aggiornare il riepilogo
            else:
                st.error("Seleziona almeno un file prima di importare.")
    else:
        st.warning("Nessun file disponibile per l'importazione. Assicurati che i file siano nella directory corrente e rispettino il formato 'validtickers_XXX_XXX.xlsx' o 'validtickers_XXX_XXX.xls'.")

    # Visualizzazione del riepilogo dei ticker presenti nel database
    st.header("📊 Riepilogo dei Ticker nel Database")
    tickers = db_tickers.get_all_tickers()

    if tickers:
        df = pd.DataFrame(tickers, columns=["ID", "Ticker", "Name", "Nation", "Instrument_Type", "Excluded"])

        # Riepilogo per Nazione e Tipo di Strumento
        summary = df.groupby(['Nation', 'Instrument_Type']).size().reset_index(name='Count')
        st.markdown("### Numero di Ticker per Nazione e Tipo di Strumento")
        st.dataframe(summary)

        # Calcola il numero totale di ticker nel database
        total_tickers = len(df)
        st.markdown(f"**Numero Totale di Ticker nel Database:** {total_tickers}")

        # Riepilogo dei ticker esclusi per mercato e strumento
        st.header("📉 Ticker Esclusi per Nazione e Strumento")
        excluded_summary = df[df['Excluded'] == 1].groupby(['Nation', 'Instrument_Type']).size().reset_index(name='Excluded Count')

        # Gestione della visualizzazione dei ticker esclusi
        for index, row in excluded_summary.iterrows():
            nation = row['Nation']
            instrument_type = row['Instrument_Type']
            excluded_count = row['Excluded Count']

            if f"{nation}_{instrument_type}_shown" not in st.session_state:
                st.session_state[f"{nation}_{instrument_type}_shown"] = False

            if st.button(f"Visualizza Ticker Esclusi: {nation} - {instrument_type} ({excluded_count} esclusi)", key=f"btn_{nation}_{instrument_type}"):
                st.session_state[f"{nation}_{instrument_type}_shown"] = True

            # Visualizza i ticker esclusi quando si clicca il pulsante
            if st.session_state[f"{nation}_{instrument_type}_shown"]:
                filtered_excluded_df = df[(df['Excluded'] == 1) &
                                          (df['Nation'] == nation) &
                                          (df['Instrument_Type'] == instrument_type)]
                st.markdown(f"### Ticker Esclusi per {nation} - {instrument_type}")
                st.dataframe(filtered_excluded_df)

                # Aggiungi la possibilità di modificare il flag di esclusione
                st.header("⚙️ Modifica Flag Esclusione per Ticker")
                modified_excluded = {}

                # Inizializza lo stato dei checkbox prima di renderli
                for idx, ticker_row in filtered_excluded_df.iterrows():
                    ticker_id = ticker_row["ID"]
                    excluded = ticker_row["Excluded"]

                    # Inizializzare lo stato nel session_state solo se non esiste già
                    if f"ticker_{ticker_id}" not in st.session_state:
                        st.session_state[f"ticker_{ticker_id}"] = excluded == 1

                    checkbox_label = f"{ticker_row['Ticker']} - {ticker_row['Name']}"
                    modified_excluded[ticker_id] = st.checkbox(f"Reimposta {checkbox_label}",
                                                               value=st.session_state[f"ticker_{ticker_id}"],
                                                               key=f"ticker_{ticker_id}")

                # Salva le modifiche apportate
                if st.button(f"Salva Modifiche per {nation} - {instrument_type}", key=f"save_{nation}_{instrument_type}"):
                    for ticker_id, new_excluded_value in modified_excluded.items():
                        # Aggiorna i valori solo dopo che sono stati modificati
                        db_tickers.update_excluded(ticker_id, int(new_excluded_value))
                        st.session_state[f"ticker_{ticker_id}"] = new_excluded_value
                    st.success(f"Modifiche salvate per {nation} - {instrument_type}.")
                    st.experimental_rerun()

    else:
        st.warning("Nessun ticker presente nel database. Importa i dati prima di procedere.")

    # Funzione di ricerca per Ticker o Nome
    st.header("🔍 Ricerca Ticker")
    search_term = st.text_input("Cerca per Ticker o Nome")

    if search_term:
        filtered_df = df[(df['Ticker'].str.contains(search_term, case=False, na=False)) |
                         (df['Name'].str.contains(search_term, case=False, na=False))]
        st.markdown(f"### Risultati della Ricerca per '{search_term}':")
        st.dataframe(filtered_df)

        if not filtered_df.empty:
            st.header("⚙️ Modifica Esclusione Ticker")

            modified_excluded = {}
            for index, row in filtered_df.iterrows():
                ticker_id = row["ID"]
                excluded = row["Excluded"]

                if f"ticker_{ticker_id}" not in st.session_state:
                    st.session_state[f"ticker_{ticker_id}"] = excluded == 1

                checkbox_label = f"{row['Ticker']} - {row['Name']} ({row['Nation']}, {row['Instrument_Type']})"
                modified_excluded[ticker_id] = st.checkbox(f"Escludi {checkbox_label}",
                                                           value=st.session_state[f"ticker_{ticker_id}"],
                                                           key=str(ticker_id))

            if st.button("Salva Modifiche Esclusione"):
                for ticker_id, new_excluded_value in modified_excluded.items():
                    db_tickers.update_excluded(ticker_id, int(new_excluded_value))
                    st.session_state[f"ticker_{ticker_id}"] = new_excluded_value
                st.success("Le modifiche di esclusione sono state salvate con successo.")
                st.experimental_rerun()
        else:
            st.warning("Nessun titolo trovato nei risultati della ricerca.")

    # Funzione di cancellazione dei ticker per mercato
    st.header("🗑️ Cancella Ticker per Mercato")

    available_nations = sorted(set(df['Nation']))
    available_instruments = sorted(set(df['Instrument_Type']))

    if available_nations and available_instruments:
        selected_nation = st.selectbox("Seleziona la Nazione", [""] + available_nations)
        selected_instrument_type = st.selectbox("Seleziona il Tipo di Strumento", [""] + available_instruments)

        if st.button("Cancella Mercato"):
            if selected_nation or selected_instrument_type:
                db_tickers.delete_market(nation=selected_nation if selected_nation else None,
                                         instrument_type=selected_instrument_type if selected_instrument_type else None)
                st.success(f"Ticker per il mercato '{selected_nation}' e tipo di strumento '{selected_instrument_type}' cancellati con successo.")
                st.experimental_rerun()
            else:
                st.error("Seleziona almeno la nazione o il tipo di strumento per procedere con la cancellazione.")
    else:
        st.warning("Nessun mercato o strumento disponibile per la cancellazione. Importa i dati prima di procedere.")

    # Visualizza i ticker presenti nel database in una tabella completa
    st.header("📋 Ticker nel Database")
    if tickers:
        st.dataframe(df)
    else:
        st.warning("Nessun ticker presente nel database.")


valid_tickers_page()
