import streamlit as st
from Ticker import Ticker


def page_ticker_summary(selected_ticker):
    # Verifica che il ticker sia valido
    if not selected_ticker:
        st.error("Ticker non selezionato.")
        return

    st.title(f"Dettagli del Ticker: {selected_ticker}")

    # Esegui il recupero e la visualizzazione dei dati del ticker
    try:
        ticker_instance = Ticker(ticker=selected_ticker)
        ticker_instance.generateTickerTAindicatorsScoringandSignals(period='2y')

        # Visualizza i dettagli del ticker
        st.write(f"Close: {ticker_instance.close}")
        st.write(f"Scoring: {ticker_instance.scoring}")
        st.write(f"Signal6: {ticker_instance.signal6}")
        st.write(f"Percent Change 2: {ticker_instance.percent_change_2}%")
        st.write(f"Percent Change 5: {ticker_instance.percent_change_5}%")
        st.write(f"Percent Change 10: {ticker_instance.percent_change_10}%")

    except Exception as e:
        st.error(f"Errore nel recupero dei dati del ticker: {e}")
