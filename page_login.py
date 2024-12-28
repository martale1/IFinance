from utils import read_last_line_content_in_brackets, read_last_lines_of_log

from charts import charts
import streamlit as st
from dbUsers import dbUsers
from User import User
from messaging import messaging
#from dbTickersData import dbTickersData
import pandas as pd
from dbWatchlist import dbWatchlist
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
def display_all_watchlist_stocks(selected_columns):
    """
    Display all stocks from the user's watchlists with the specified columns.
    Allow the user to select a stock from a dropdown or type the ticker name to display its chart.

    Args:
        selected_columns (list): The column order of the selected watchlist.
    """


    # Initialize database classes
    db_watchlist = dbWatchlist()
    db_tickers_data = dbTickersData()

    # Retrieve all watchlists for the user
    watchlists = db_watchlist.get_watchlists("mau")
    all_tickers_data = []

    if watchlists:
        for watchlist in watchlists:
            watchlist_name = watchlist[0]
            tickers = db_watchlist.get_tickers_in_watchlist("mau", watchlist_name)
            tickers = [ticker[0] for ticker in tickers if ticker[0]]

            for ticker_symbol in tickers:
                try:
                    ticker_info = db_tickers_data.load_json_data(ticker_symbol)
                    if ticker_info:
                        all_tickers_data.append([
                            ticker_info['ticker'],
                            ticker_info['signals'][0]['Percent_Change_2'],
                            ticker_info['signals'][0]['Scoring'],
                            ticker_info['signals'][0]['Signal6'],
                            ticker_info['signals'][0]['Percent_Change_5'],
                            ticker_info['signals'][0]['Percent_Change_10'],
                            ticker_info['signals'][0]['Percent_Change_30'],
                            int(ticker_info['signals'][0]['Volume']),
                            ticker_info['signals'][0]['ADX'],
                            ticker_info['signals'][0]['MACD_Histogram'],
                            ticker_info['signals'][0]['RSI'],
                            ticker_info['signals'][0]['Signal1'],
                            ticker_info['signals'][0]['Signal2'],
                            ticker_info['signals'][0]['Signal3'],
                            ticker_info['signals'][0]['Signal4'],
                            ticker_info['signals'][0]['Signal5'],
                            ticker_info['signals'][0]['Close'],
                            ticker_info['ticker_name']
                        ])
                except Exception as e:
                    st.warning(f"Error loading data for {ticker_symbol}: {e}")

        if all_tickers_data:
            # Create a DataFrame
            ticker_df = pd.DataFrame(all_tickers_data, columns=[
                "Ticker", "var%2d", "Scoring", "Signal6", "var%5d", "var%10d", "var%30d", "Volume",
                "ADX", "MACDH", "RSI", "Signal1", "Signal2", "Signal3", "Signal4", "Signal5", "Close", "Ticker Name"
            ])

            # Ensure the column order matches the selected watchlist
            ticker_df = ticker_df[selected_columns]

            # Convert necessary columns to numeric
            numeric_columns = ["var%2d", "var%5d", "var%10d", "var%30d", "ADX", "MACDH", "RSI", "Close", "Volume"]
            for col in numeric_columns:
                ticker_df[col] = pd.to_numeric(ticker_df[col], errors='coerce')

            # Format the DataFrame to show two decimal places for numeric columns
            formatted_df = (
                ticker_df.style
                .format(
                    {
                        "var%2d": "{:.2f}",
                        "var%5d": "{:.2f}",
                        "var%10d": "{:.2f}",
                        "var%30d": "{:.2f}",
                        "ADX": "{:.2f}",
                        "MACDH": "{:.2f}",
                        "RSI": "{:.2f}",
                        "Close": "{:.2f}",
                        "Volume": "{:,.0f}",  # No decimal for volume
                    },
                    na_rep="-"
                )
                .applymap(
                    lambda val: 'color: green' if isinstance(val, (float, int)) and val > 0 else 'color: red',
                    subset=["var%2d", "var%5d", "var%10d", "var%30d", "ADX", "MACDH", "RSI", "Close"]
                )
            )

            st.markdown("### 📜 Watchlist Stocks")
            st.dataframe(formatted_df, use_container_width=True)

            # Input for typing a ticker name
            st.markdown("### Type the ticker to chart")
            typed_ticker = st.text_input("Type a ticker name:")

            # Dropdown for selecting a ticker (sorted alphabetically)
            st.markdown("### 📈 Select a Stock to chart")
            sorted_tickers = sorted(ticker_df["Ticker"].tolist())
            selected_ticker = st.selectbox("Select a ticker:", [""] + sorted_tickers)

            # Determine which ticker to use for the chart
            ticker_to_display = typed_ticker.upper() if typed_ticker else selected_ticker

            if ticker_to_display:
                if ticker_to_display in ticker_df["Ticker"].values:
                    ticker_name = ticker_df.loc[ticker_df["Ticker"] == ticker_to_display, "Ticker Name"].values[0]
                    st.markdown(f"**Selected Ticker:** {ticker_to_display} - {ticker_name}")
                    tchart = charts(ticker_to_display)
                    tchart.plot_ticker_price_and_macd()
                    tchart.plot_candlestick_chart(50)
                else:
                    st.warning(f"Ticker '{ticker_to_display}' not found in the watchlists.")
        else:
            st.warning("No tickers found in your watchlists.")
    else:
        st.warning("You have no watchlists. Please create one to view stocks.")

def display_top5_stocks(category, nation="IT", days=2):
    """
    Display the top 5 stocks for a given category (ETF, ETC, MIB30).

    Args:
        category (str): The category for which to fetch top 5 stocks (e.g., ETC, ETF, MIB30).
        nation (str): Nation filter, defaults to "IT".
        days (int): The number of days for percentage change, defaults to 2.
    """
    # Initialize the database instance
    myDb = dbTickersData()

    # Fetch top 5 stocks for the specified category
    top5 = myDb.get_top_n_tickers_by_percent_change(nation, category, days, limit=5)

    if top5:
        # Convert the results into a DataFrame for display
        df = pd.DataFrame(top5, columns=["Ticker", "Name", f"{days}-Day % Change"])

        # Format the percentage change column to 2 decimal places
        df[f"{days}-Day % Change"] = df[f"{days}-Day % Change"].apply(lambda x: f"{x:.2f}")

        # Display the results in a table
        st.subheader(f"Top 5 for {category}")
        st.table(df)
    else:
        st.subheader(f"Top 5 for {category}")
        st.write("No data available.")

    # Ensure the database connection is closed
    myDb.close()


import streamlit as st
import pandas as pd
from dbTickersDataOLD2 import dbTickersData  # Assuming your database class is here


def visualizza_top_tickers(market_name, market_category, n=5, min_volume=1500):
    """
    Display the top N tickers for a given market category (e.g., ETC, ETF, MIB30).

    Args:
        market_name (str): Display name for the market (e.g., "IT - ETC").
        market_category (str): Database category (e.g., "ETC", "ETF", "MIB30").
        n (int): Number of top tickers to display. Default is 5.
        min_volume (int): Minimum volume to filter tickers. Default is 1500.
    """
    # Database instance
    db = dbTickersData()

    # Header with styled title
    st.markdown(f"""
        <div style='background: linear-gradient(to right, #4facfe, #00f2fe); padding: 10px; border-radius: 10px;'>
            <h2 style='color: white; font-size: 24px; text-align: center;'>{market_name}</h2>
        </div>
    """, unsafe_allow_html=True)

    # Fetch sorted tickers
    ticker_data_df = db.get_sorted_tickers_by_keys(
        nation="IT",
        instrument_type=market_category,
        primary_key="percent_change_2",
        secondary_key="volume",
        additional_columns=["volume", "signal6", "percent_change_2", "scoring"],
        min_volume=min_volume,
    )

    # Ensure proper data types for calculations
    ticker_data_df['percent_change_2'] = pd.to_numeric(ticker_data_df['percent_change_2'], errors='coerce')
    ticker_data_df['scoring'] = pd.to_numeric(ticker_data_df['scoring'], errors='coerce')

    # Sort by primary and secondary keys
    ticker_data_df = ticker_data_df.sort_values(by=["percent_change_2", "volume"], ascending=[False, False])

    # Signal colors
    signal_colors = {
        'Uptrend': "🟢", 'Uptrend*': "🟢", 'Uptrend-': "🟢", 'uptrend--': "🟢", 'uptrend---': "🟢",
        'wakeup2': "🟠", 'wakeup2*': "🟠", 'wakeup2-': "🟠", 'wakeup1': "🟠", 'wakeup-1': "🟠",
        'sleep1': "🟠", 'sleep2': "🟠",
        'Downtrend': "🔴", 'Downtrend*': "🔴", 'Downtrend_revS3Sig+': "🔴", 'Downtrend_revS3Sig++': "🔴",
        'Downtrend_revS3Sig+++': "🔴",
    }

    # Display the top N tickers
    if not ticker_data_df.empty:
        for i, row in ticker_data_df.head(n).iterrows():
            ticker = row['Ticker']
            ticker_name = row['Ticker_Name']
            percent_change = row['percent_change_2']
            volume = row['volume']
            scoring = row['scoring']
            signal6 = row['signal6']

            # Render ticker row with formatted details
            signal_emoji = signal_colors.get(signal6, "⚪")
            button_label = (
                f"**{ticker}** | {ticker_name}, "
                f"**{percent_change:.2f}%**, "
                f"Volume: {int(volume):,}, "
                f"Scoring: {int(scoring)}, "
                f"Signal: {signal_emoji} {signal6}"
            )

            # Unique key for the button
            if st.button(button_label, key=f"{market_category}_{ticker}_{i}"):
                st.success(f"Displaying chart for {ticker}")
                st.session_state['display_chart'] = ticker
                st.experimental_rerun()
    else:
        st.write(f"No data available for {market_name} with a minimum volume of {min_volume}")

    # Close the database connection
    db.close()


def login_page():
    # Inizializzazione della classe dbUsers
    db_users = dbUsers()

    # Impostazioni della pagina (Chiamala solo se non è già stata chiamata in `main_app.py`)
    st.title("IFinance Login:")


    # Campi di input per il login
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    st.session_state["user_email"] =""
    if st.button("Login"):
        if 'display_chart' in st.session_state:
            del st.session_state['display_chart']
        user = db_users.get_user(login_email)
        if user and user[3] == User._encrypt_password(None, login_password):  # Confronta la password cifrata
            if (user[0])!="mau":
                ms = messaging()
                ms.send("User connected:"+user[0])
            #st.success("Cookie impostato!")
            st.success(f"Benvenuto, {user[0]} {user[1]}!")
            # Imposta l'email dell'utente nella sessione
            st.session_state["user_email"] = login_email
            # Reindirizza alla pagina di gestione del portafoglio
            st.session_state.query_params = {"page": "insights"}
            #st.experimental_rerun()  # Ricarica la pagina con i nuovi parametri
            st.rerun()
        else:
            st.error("Wrong Email of Password.")

        # Divider
    if  'display_chart' in st.session_state:
        st.write(st.session_state['display_chart'])
        tchart1 = charts(st.session_state['display_chart'],'2y',1)
        tchart1.plot_ticker_price_and_macd()
        #tchart1.plot_candlestick_chart(50)

    st.markdown("---")

    # Preview the top 5 stocks for ETC, ETF, and MIB30
    st.subheader("Best 5 of the day")
    #display_top5_stocks("ETC")  # Show top 5 for ETC
    #display_top5_stocks("ETF")  # Show top 5 for ETF
    #display_top5_stocks("MIB30")  # Show top 5 for MIB30
    visualizza_top_tickers("IT - ETC", "ETC", n=8)
    visualizza_top_tickers("IT - ETF", "ETF", n=8)
    visualizza_top_tickers("IT - MIB30", "MIB30", n=8)

    #Visualizza segnali
    visualizza_titoli_per_segnali()

    #### Visualizza mia watchlist
    selected_columns = ["Ticker", "var%2d", "Scoring","Signal2", "Signal3", "Signal6",  "ADX","var%5d", "var%10d", "var%30d",
                        "Volume", "MACDH", "RSI", "Signal1",
                        "Signal4", "Signal5", "Close", "Ticker Name"]
    display_all_watchlist_stocks(selected_columns)

    #Visualizza best scoring
    visualizza_best_scoring(10)

