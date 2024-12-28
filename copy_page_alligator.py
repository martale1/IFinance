import streamlit as st
import pandas as pd
from dbTickersDataOLD2 import dbTickersData
from charts import charts


def page_alligator():
    # Inizializza l'istanza del database
    myDb = dbTickersData()

    # Sidebar per controlli e navigazione
    with st.sidebar:
        # Visualizza l'email dell'utente
        user_email = st.session_state.get("user_email", "Utente")
        st.markdown(f"**User: {user_email}**")

        # Filtri dinamici
        nation = st.selectbox("Select the nation", options=["IT"], index=0)
        instrument_type = st.selectbox("Instrument type", options=["ETC", "ETF", "MIB30"], index=0)

        # Input per il numero di ticker da visualizzare
        n_value = st.text_input("Number of tickers to visualize:", value="300")
        n_value = int(n_value) if n_value.isdigit() else 10

        # Pulsanti per navigazione
        if st.button("Insights"):
            st.session_state.query_params = {"page": "insights"}
            st.rerun()

        if st.button("Signals"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "signals"}
            st.rerun()

        if st.button("Watchlist"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "watchlist"}
            st.rerun()

        if st.button("Portfolio"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "portfolio"}
            st.rerun()

        if st.button("Logout"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.clear()
            st.session_state.query_params = {"page": "login"}
            st.rerun()

    # Corpo della pagina
    st.title("Stock Insights - Alligator Page")

    # Recupera i dati utilizzando la funzione get_sorted_tickers_by_signal6
    sorted_tickers = myDb.get_sorted_tickers_by_signal6(
        nation=nation,
        instrument_type=instrument_type,
        secondary_key="scoring",
        additional_columns=["Percent_Change_2", "Signal2", "Signal3", "Signal5", "Volume","adx", "Signal1", "Signal4", "stochastic_k","RSI", "ticker_name"]
    )

    if not sorted_tickers.empty:
        # Converte le colonne Signal1-Signal5 in numeri
        for col in ["Signal1", "Signal2", "Signal3", "Signal4", "Signal5"]:
            sorted_tickers[col] = pd.to_numeric(sorted_tickers[col], errors='coerce')

        # **Selezione Classe Signal6**
        signal6_classes = ["All", "Segnali > 0"] + sorted_tickers['Signal6'].unique().tolist()
        selected_signal6 = st.selectbox("Select signal6 class", options=signal6_classes)

        # Filtra i dati in base alla selezione
        if selected_signal6 == "Segnali > 0":
            sorted_tickers = sorted_tickers[
                (sorted_tickers['Signal1'] > 0) |
                (sorted_tickers['Signal2'] > 0) |
                (sorted_tickers['Signal3'] > 0) |
                (sorted_tickers['Signal4'] > 0) |
                (sorted_tickers['Signal5'] > 0)
            ]
        elif selected_signal6 != "All":
            sorted_tickers = sorted_tickers[sorted_tickers['Signal6'] == selected_signal6]

        # Limita il numero di risultati in base a n_value
        sorted_tickers_limited = sorted_tickers.head(n_value)

        # Rinomina le colonne per la tabella dei tickers
        column_mapping = {
            "Percent_Change_2": "p2d%",
            "Signal2": "s2",
            "Signal3": "s3",
            "Signal5": "s5",
            "Volume": "V",
            "adx":"adx",
            "Signal1": "s1",
            "Signal4": "s4",
            "stochastic_k":"sk",
            "RSI": "RSI",
            "ticker_name": "ticker_name"
        }
        sorted_tickers_limited = sorted_tickers_limited.rename(columns=column_mapping)


        sorted_tickers_limited['sk'] = sorted_tickers_limited['sk'].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) else x)

        # Formatta "p2d%" con due cifre decimali
        sorted_tickers_limited['p2d%'] = sorted_tickers_limited['p2d%'].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) else x)
        # Converte "Volume" in interi come numeri
        sorted_tickers_limited['V'] = sorted_tickers_limited['V'].apply(lambda x: int(float(x)) if pd.notnull(x) else x)

        # Funzione per applicare stile alla colonna "p2d%"
        def highlight_percent_change(val):
            try:
                val = float(val)
                color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                return f'color: {color}'
            except ValueError:
                return ''

        # Applica lo stile alla tabella
        styled_tickers = sorted_tickers_limited.style.applymap(
            highlight_percent_change, subset=['p2d%']
        )

        # Visualizza la tabella con stile
        st.subheader(f"Ordered tickers ({nation} - {instrument_type} - Class: {selected_signal6})")
        st.dataframe(styled_tickers, use_container_width=True)

        # Selezione del ticker per il grafico
        sel_ticker = st.selectbox("Select the ticker to plot", [""] + list(sorted_tickers_limited['Ticker']))
        if sel_ticker:
            st.markdown(f"**Chart for the selected ticker: {sel_ticker}**")
            tchart = charts(sel_ticker)
            tchart.plot_ticker_price_and_macd()
            tchart.plot_candlestick_chart(50)



    else:
        st.warning("No results.")

    # **Tabella con la distribuzione per Signal6 (in fondo alla pagina)**
    if not sorted_tickers.empty:
        st.divider()  # Aggiunge una linea divisoria

        signal6_counts = sorted_tickers['Signal6'].value_counts().reset_index()
        signal6_counts.columns = ['Signal6', 'Count']

        # Calcolo del totale
        total_count = signal6_counts['Count'].sum()

        # Calcolo della percentuale rispetto al totale
        signal6_counts['Percentage'] = (signal6_counts['Count'] / total_count) * 100

        # Visualizza la tabella con i conteggi
        st.subheader(f"Tickers distributions by signal6 ({nation} - {instrument_type})")
        st.dataframe(signal6_counts)



        # Visualizza il totale generale
        st.text(f"Total: {total_count}")

    # Chiudi la connessione al database
    myDb.close()


# Esegui la funzione per la pagina
if __name__ == "__main__":
    page_alligator()
