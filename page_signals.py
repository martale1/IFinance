from utils import read_last_line_content_in_brackets, read_last_lines_of_log
from charts import charts
from dbTickersData import dbTickersData
import streamlit as st


db = dbTickersData()

def read_last_lines_of_log(file_path, num_lines=3):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return lines[-num_lines:] if len(lines) >= num_lines else lines
    except FileNotFoundError:
        return ["Log file not found."]

def visualizza_titoli_per_segnali():
    # Titolo con uno stile migliorato
    st.write("Last processing: " + read_last_line_content_in_brackets())

    st.markdown("""
        <div style='background: linear-gradient(to right, #4facfe, #00f2fe); padding: 5px; border-radius: 10px;'>
            <h1 style='color: white; font-size: 28px; text-align: center;'>Signals (S1, S2, S3, S4, S5)</h1>
        </div>
    """, unsafe_allow_html=True)

    # Mappatura dei colori per il segnale signal6
    signal_colors = {
        'Uptrend': "🟢", 'Uptrend*': "🟢", 'Uptrend-': "🟢", 'uptrend--': "🟢", 'uptrend---': "🟢",  # Uptrend (verde)
        'wakeup2': "🟠", 'wakeup2*': "🟠", 'wakeup2-': "🟠", 'wakeup1': "🟠", 'wakeup-1': "🟠",  # Wakeup (arancione)
        'sleep1': "🟠", 'sleep2': "🟠",  # Sleep (arancione)
        'Downtrend': "🔴", 'Downtrend*': "🔴", 'Downtrend_revS3Sig+': "🔴", 'Downtrend_revS3Sig++': "🔴",
        'Downtrend_revS3Sig+++': "🔴"  # Downtrend (rosso)
    }

    # Funzione per visualizzare i titoli per un determinato mercato e segnale
    def show_signals_for_market(nation, instrument_type):
        # Recupera i dati, inclusi volume, percent_change_2, signal6 e scoring
        (df_count_1, df_count_neg_1, df_tickers_1, df_ticker_names_1,
         df_volume, df_percent_change_2, df_signal6, df_scoring) = db.get_signal_counts_and_ticker_lists(nation,
                                                                                                          instrument_type)

        # Funzione helper per creare il testo del pulsante con le informazioni aggiuntive e la colorazione
        def create_button_label(ticker, ticker_name, volume, percent_change_2, signal6, scoring):
            percent_change_str = f"**{float(percent_change_2):.2f}%**"
            scoring_str = f"**Scoring: {int(scoring)}**"
            volume_str = f"V={float(volume):,.0f}"
            signal_emoji = signal_colors.get(signal6, "⚪")
            signal_str = f"{signal_emoji} {signal6}"
            jsonTicker=db.load_json_data(ticker)
            signal3 = jsonTicker['signals'][0]['Signal3']
            signal2 = jsonTicker['signals'][0]['Signal2']
            signal5 = jsonTicker['signals'][0]['Signal5']


            return f"**{ticker}**, {ticker_name}, s2={signal2}, s3={signal3}, s5={signal5},  {scoring_str}| {percent_change_str}, {volume_str}, {signal_str}"

        # Recupera i ticker e i nomi per ciascun segnale come liste
        tickers_s1 = list(zip(df_tickers_1['S1'][0].split(', '), df_ticker_names_1['S1'][0].split(', '),
                              df_volume['S1'][0].split(', '), df_percent_change_2['S1'][0].split(', '),
                              df_signal6['S1'][0].split(', '), df_scoring['S1'][0].split(', ')))

        tickers_s2 = list(zip(df_tickers_1['S2'][0].split(', '), df_ticker_names_1['S2'][0].split(', '),
                              df_volume['S2'][0].split(', '), df_percent_change_2['S2'][0].split(', '),
                              df_signal6['S2'][0].split(', '), df_scoring['S2'][0].split(', ')))

        tickers_s3 = list(zip(df_tickers_1['S3'][0].split(', '), df_ticker_names_1['S3'][0].split(', '),
                              df_volume['S3'][0].split(', '), df_percent_change_2['S3'][0].split(', '),
                              df_signal6['S3'][0].split(', '), df_scoring['S3'][0].split(', ')))

        tickers_s4 = list(zip(df_tickers_1['S4'][0].split(', '), df_ticker_names_1['S4'][0].split(', '),
                              df_volume['S4'][0].split(', '), df_percent_change_2['S4'][0].split(', '),
                              df_signal6['S4'][0].split(', '), df_scoring['S4'][0].split(', ')))

        tickers_s5 = list(zip(df_tickers_1['S5'][0].split(', '), df_ticker_names_1['S5'][0].split(', '),
                              df_volume['S5'][0].split(', '), df_percent_change_2['S5'][0].split(', '),
                              df_signal6['S5'][0].split(', '), df_scoring['S5'][0].split(', ')))

        # Funzione per mostrare i ticker con le informazioni aggiuntive per ogni segnale
        def display_signals(signals, signal_name, signal_description, signal_count):
            with st.expander(f"{signal_name} (**{signal_count}** tickers: {signal_description})"):
                for i, (ticker, ticker_name, volume, percent_change_2, signal6, scoring) in enumerate(signals):
                    if ticker.strip():
                        button_label = create_button_label(ticker, ticker_name, volume, percent_change_2, signal6,
                                                           scoring)
                        if st.button(button_label, key=f"{nation}_{instrument_type}_{signal_name}_{i}"):
                            st.markdown(f"**Visualizzazione grafico per {ticker} ({ticker_name})**")
                            st.session_state['display_chart'] = ticker
                            st.rerun()

        # Conteggi delle occorrenze per ciascun segnale
        count_s1, count_s2, count_s3, count_s4, count_s5 = map(len, [tickers_s1, tickers_s2, tickers_s3, tickers_s4,
                                                                     tickers_s5])

        # Visualizza i ticker con le informazioni aggiuntive per ciascun segnale
        display_signals(tickers_s1, "S1", "macd crossing signal", count_s1)
        display_signals(tickers_s2, "S2", "sk crossing above 20", count_s2)
        display_signals(tickers_s3, "S3", "macd crossing above  0", count_s3)
        display_signals(tickers_s4, "S4", "rsi crossing above 50", count_s4)
        display_signals(tickers_s5, "S5", "crossing bollinger", count_s5)

    # Sezione per IT - ETC
    st.markdown("<h2 style='color: green; font-size: 24px;'>IT - ETC</h2>", unsafe_allow_html=True)
    show_signals_for_market("IT", "ETC")

    # Sezione per IT - ETF
    st.markdown("<h2 style='color: purple; font-size: 24px;'>IT - ETF</h2>", unsafe_allow_html=True)
    show_signals_for_market("IT", "ETF")

    # Sezione per IT - MIB30
    st.markdown("<h2 style='color: orange; font-size: 24px;'>IT - MIB30</h2>", unsafe_allow_html=True)
    show_signals_for_market("IT", "MIB30")








def page_signals():
    # Titolo della pagina
    st.title("Signals")
    if  'display_chart' in st.session_state:
        st.write(st.session_state['display_chart'])
        tchart1 = charts(st.session_state['display_chart'])
        tchart1.plot_ticker_price_and_macd()
        tchart1.plot_candlestick_chart(50)




    ### Visualizza dati per i tre mercati principali
    # Sposta i pulsanti nella sidebar
    with st.sidebar:


        user_email = st.session_state.get("user_email", "Utente")
        st.markdown(f"**User: {user_email}**")

        #n_value = st.text_input("Numero di ticker da visualizzare", value="6")
        #n_value=int(n_value)

        if st.button("Insights"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "insights"}
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





    visualizza_titoli_per_segnali()
    # Parametri di filtro
    st.subheader("Market details")

    nation = st.selectbox("Select the nation", options=["IT", "US"], index=0)
    instrument_type = st.selectbox("Instrument type", options=["ETC", "ETF", "MIB30"], index=0)
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
        st.write(f"Ordered list")
        st.dataframe(results_df, use_container_width=True)
    else:
        st.warning("No results.")

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



    st.markdown("## Last 3 Log Entries")
    log_lines = read_last_lines_of_log("/home/developer/PycharmProjects/learningProjects/IFinance/run_log.txt",1)
    for line in log_lines:
        st.text(line)

