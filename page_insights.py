from utils import read_last_line_content_in_brackets, read_last_lines_of_log
from charts import charts
from dbTickersData import dbTickersData
import streamlit as st

db = dbTickersData()

def visualizza_best_of_the_day(n=5):
    # Titolo con uno stile migliorato
    st.markdown("""
        <div style='background: linear-gradient(to right, #4facfe, #00f2fe); padding: 5px; border-radius: 10px;'>
            <h1 style='color: white; font-size: 28px; text-align: center;'>Best of the day</h1>
        </div>
    """, unsafe_allow_html=True)

    # Mappatura dei colori per il segnale signal6
    signal_colors = {
        'Uptrend': "🟢", 'Uptrend*': "🟢", 'Uptrend-': "🟢", 'uptrend--': "🟢", 'uptrend---': "🟢",  # Uptrend (verde)
        'wakeup2': "🟠", 'wakeup2*': "🟠", 'wakeup2-': "🟠", 'wakeup1': "🟠", 'wakeup-1': "🟠",  # Wakeup (arancione)
        'sleep1': "🟠", 'sleep2': "🟠",  # Sleep (arancione)
        'Downtrend': "🔴", 'Downtrend*': "🔴", 'Downtrend_revS3Sig+': "🔴", 'Downtrend_revS3Sig++': "🔴", 'Downtrend_revS3Sig+++': "🔴"  # Downtrend (rosso)
    }

    # Funzione per formattare i dati del ticker con colori per signal6 e scoring
    def render_ticker_row(ticker, name, percent_change, volume, signal6, scoring):
        percent_change_str = f"**{float(percent_change):.2f}%**"  # Evidenzia la variazione percentuale
        volume_str = f"V={float(volume):,.0f}"  # Formatta il volume con separatore delle migliaia
        scoring_str = f"**Scoring: {int(scoring)}**"  # Evidenzia lo scoring in grassetto
        signal_emoji = signal_colors.get(signal6, "⚪")  # Ottieni il colore in base a signal6, predefinito bianco
        signal_str = f"{signal_emoji} {signal6}"  # Formatta il segnale
        # Evidenzia il ticker in grassetto
        jsonTicker = db.load_json_data(ticker)
        signal3 = jsonTicker['signals'][0]['Signal3']
        signal2 = jsonTicker['signals'][0]['Signal2']
        signal5 = jsonTicker['signals'][0]['Signal5']


        button_label = f"**{ticker}**, {name}, {scoring_str}| {percent_change_str}, {volume_str}, s2={signal2}, s3={signal3}, s5={signal5}  {signal_str}"
        return button_label

    # Funzione helper per mostrare i migliori ticker per ogni mercato
    def show_top_tickers_for_market(market_name, ticker_market, color_class):
        st.markdown(f"<h2 style='color: {color_class}; font-size: 24px;'>{market_name}</h2>", unsafe_allow_html=True)
        ticker_data_df = db.get_sorted_tickers_by_keys("IT", ticker_market, "percent_change_2", "volume",
                                                    ["volume", "signal6", "percent_change_2", "scoring"], min_volume=1500)
        # Assicurati che 'scoring' e 'percent_change_2' siano trattati come numeri (float)
        #ticker_data_df['percent_change_2'] = pd.to_numeric(ticker_data_df['percent_change_2'], errors='coerce')

        # Ordina prima per 'scoring' (decrescente) e poi per 'percent_change_2' (decrescente)
        #ticker_data = ticker_data_df.sort_values(by=['percent_change_2'], ascending=[False])
        ticker_data=ticker_data_df
        if not ticker_data.empty:
            for i, ticker_row in enumerate(ticker_data.head(n).itertuples()):
                # Usa replace per rimuovere spazi interni e garantire che il ticker sia unico
                ticker_cleaned = ticker_row.Ticker.replace(" ", "")
                button_label = render_ticker_row(ticker_cleaned, ticker_row.Ticker_Name, ticker_row.percent_change_2,
                                                 ticker_row.volume, ticker_row.signal6, ticker_row.scoring)
                # Aggiungi una chiave univoca al pulsante, utilizzando `i` e `ticker_cleaned`
                if st.button(button_label, key=f"{market_name}_{ticker_cleaned}_{i}_{ticker_row.Ticker_Name}"):
                    st.markdown(f"**Displaying chart for {ticker_cleaned}**")
                    st.session_state['display_chart'] = ticker_cleaned
                    st.rerun()

        else:
            st.write(f"Nessun dato disponibile per {market_name} con volume maggiore di 1500")

    # Mostra i migliori ticker per IT - ETC
    show_top_tickers_for_market("IT - ETC", "ETC", "green")

    # Mostra i migliori ticker per IT - ETF
    show_top_tickers_for_market("IT - ETF", "ETF", "purple")

    # Mostra i migliori ticker per IT - MIB30
    show_top_tickers_for_market("IT - MIB30", "MIB30", "orange")




def visualizza_best_scoring(n=5):
    # Titolo con uno stile migliorato
    #st.session_state['selected_watchlist'] = "Entrato in scoring"

    st.markdown("""
        <div style='background: linear-gradient(to right, #f0ad4e, #ff5722); padding: 10px; border-radius: 10px;'>
            <h1 style='color: white; font-size: 28px; text-align: center;'>Best scoring</h1>
        </div>
    """, unsafe_allow_html=True)

    # Mappatura dei colori per il segnale signal6
    signal_colors = {
        'Uptrend': "🟢", 'Uptrend*': "🟢", 'Uptrend-': "🟢", 'uptrend--': "🟢", 'uptrend---': "🟢",  # Uptrend (verde)
        'wakeup2': "🟠", 'wakeup2*': "🟠", 'wakeup2-': "🟠", 'wakeup1': "🟠", 'wakeup-1': "🟠",  # Wakeup (arancione)
        'sleep1': "🟠", 'sleep2': "🟠",  # Sleep (arancione)
        'Downtrend': "🔴", 'Downtrend*': "🔴", 'Downtrend_revS3Sig+': "🔴", 'Downtrend_revS3Sig++': "🔴", 'Downtrend_revS3Sig+++': "🔴"  # Downtrend (rosso)
    }

    # Funzione per formattare i dati del ticker con colori per signal6, scoring e variazione percentuale
    def render_ticker_row(ticker, name, scoring, percent_change, volume, signal6):
        percent_change_str = f"**{float(percent_change):.2f}%**"  # Evidenzia la variazione percentuale in grassetto
        scoring_str = f"**Scoring: {int(scoring)}**"  # Evidenzia lo scoring in grassetto
        volume_str = f"V={float(volume):,.0f}"  # Formatta il volume con separatore delle migliaia
        signal_emoji = signal_colors.get(signal6, "⚪")  # Ottieni il colore in base a signal6, predefinito bianco
        signal_str = f"{signal_emoji} {signal6}"  # Segnale
        # Costruisci il testo del pulsante
        jsonTicker = db.load_json_data(ticker)
        signal3 = jsonTicker['signals'][0]['Signal3']
        signal2 = jsonTicker['signals'][0]['Signal2']
        button_label = f"**{ticker}**, {name}, {scoring_str}| {percent_change_str}, {volume_str},  s2={signal2}, s3={signal3} {signal_str} "
        return button_label

    # Funzione helper per mostrare i top 5 per un determinato mercato
    def show_top5_for_market(market_name, ticker_market, ticker_class):
        st.markdown(f"<h2 style='color: {ticker_class}; font-size: 24px;'>{market_name}</h2>", unsafe_allow_html=True)
        ticker_data_df = db.get_sorted_tickers_by_keys("IT", ticker_market, "scoring", "percent_change_2",
                                                    ["volume", "signal6", "scoring", "percent_change_2"], min_volume=1500)
        # Assicurati che 'scoring' e 'percent_change_2' siano trattati come numeri (float)
        #ticker_data_df['scoring'] = pd.to_numeric(ticker_data_df['scoring'], errors='coerce')
        #ticker_data_df['percent_change_2'] = pd.to_numeric(ticker_data_df['percent_change_2'], errors='coerce')

        # Ordina prima per 'scoring' (decrescente) e poi per 'percent_change_2' (decrescente)
        #ticker_data= ticker_data_df.sort_values(by=['scoring', 'percent_change_2'], ascending=[False, False])
        ticker_data=ticker_data_df
        if not ticker_data.empty:
            for i, ticker_row in enumerate(ticker_data.head(n).itertuples()):
                # Elimina spazi dal ticker prima di passarlo
                ticker_cleaned = ticker_row.Ticker.strip()
                button_label = render_ticker_row(ticker_cleaned, ticker_row.Ticker_Name, ticker_row.scoring,
                                                 ticker_row.percent_change_2, ticker_row.volume, ticker_row.signal6)
                # Aggiungi una chiave univoca al pulsante
                if st.button(button_label, key=f"{market_name}_{ticker_cleaned}_{i}"):
                    st.markdown(f"**Displaying chart for {ticker_cleaned}**")

                    st.session_state['display_chart'] = ticker_cleaned
                    st.rerun()

                    #tchart1 = charts(ticker_cleaned)
                    #tchart1.plot_ticker_price_and_macd()

        else:
            st.write(f"Nessun dato disponibile per {market_name} con volume maggiore di 1500")

    # Mostra i top 5 ticker con il miglior scoring per IT - ETC
    show_top5_for_market("IT - ETC", "ETC", "green")
    show_top5_for_market("IT - ETF", "ETF", "green")
    show_top5_for_market("IT - MIB30", "MIB30", "green")


    # Mostra i topt



def page_insights():
    # Titolo della pagina
    st.title("Insights")
    if  'display_chart' in st.session_state:
        st.write(st.session_state['display_chart'])
        tchart1 = charts(st.session_state['display_chart'],'2y',1)
        tchart1.plot_ticker_price_and_macd()
        #tchart1.plot_candlestick_chart(50)




    ### Visualizza dati per i tre mercati principali
    # Sposta i pulsanti nella sidebar
    with st.sidebar:


        user_email = st.session_state.get("user_email", "Utente")
        st.markdown(f"**User: {user_email}**")

        n_value = st.text_input("Number of tickers to display", value="10")
        n_value=int(n_value)

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

        if st.button("Alligator"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "alligator"}
            st.rerun()

        if st.button("Portfolio"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "portfolio"}
            st.rerun()  # Reindirizza alla pagina del portafoglio


        if st.button("Logout"):

            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.clear()
            st.session_state.query_params = {"page": "login"}
            st.rerun()




    st.write("Last processing: "+ read_last_line_content_in_brackets())
    visualizza_best_scoring(n=n_value)
    visualizza_best_of_the_day(n=n_value)



    # Parametri di filtro
    st.subheader("Market details")

    nation = st.selectbox("Select nation", options=["IT", "US"], index=0)
    instrument_type = st.selectbox("Select instrument (ETF,ETC..)", options=["ETC", "ETF", "MIB30"], index=0)
    primary_key = st.selectbox("Primary key",
                               options=["scoring", "signal3", "percent_change_2", "percent_change_5",
                                        "percent_change_10", "percent_change_30", "macd", "volume", "adx"], index=0)
    secondary_key = st.selectbox("Secondary key",
                                 options=["percent_change_2", "percent_change_5", "percent_change_10",
                                          "percent_change_30", "macd", "volume", "adx"], index=0)

    # Definisci le colonne aggiuntive
    if primary_key != 'volume':
        additional_columns = ['volume', 'signal6', 'signal3', 'macd']
    else:
        additional_columns = ['signal6', 'signal3', 'macd']

    # Recupera e visualizza i dati dal DB non appena la pagina viene caricata
    results_df = db.get_sorted_tickers_by_keys(
        nation=nation,
        instrument_type=instrument_type,
        primary_key=primary_key,
        secondary_key=secondary_key,
        additional_columns=additional_columns,
        min_volume=2000
    )

    # Controlla se il DataFrame è vuoto e visualizza i dati
    if not results_df.empty:
        st.write(f"Empty list")
        st.dataframe(results_df, use_container_width=True)
    else:
        st.warning("No tickers found.")

    # Input per il ticker
    ticker_symbol = st.text_input("Ticker to plot:")

    # Se l'utente ha inserito del testo, lo visualizziamo
    if ticker_symbol:
        if '.' in ticker_symbol:
            #plot_ticker_price_and_macd(ticker_symbol)
            tchart=charts(ticker_symbol)
            tchart.plot_ticker_price_and_macd()
        else:
            ticker_symbol = ticker_symbol + '.MI'
            #plot_ticker_price_and_macd(ticker_symbol)
            tchart=charts(ticker_symbol)
            tchart.plot_ticker_price_and_macd()



    st.caption("## Last 3 Log Entries")
    log_lines = read_last_lines_of_log()
    for line in log_lines:
        st.text(line)

