

import pandas as pd
from utils import read_last_line_content_in_brackets
from dbWatchlist import dbWatchlist
from charts import charts
from dbTickersData import dbTickersData
from dbValidTickers import dbValidTickers
import yfinance as yf
from GenerateScoringAndSignals import GenerateScoringAndSignals
from openaimyv1 import myOpenAIv1
from messaging import messaging
import streamlit as st


def display_all_watchlist_stocks(selected_columns):
    """
    Display all stocks from the user's watchlists with the specified columns.
    Allow the user to select a stock from a dropdown or type the ticker name to display its chart.

    Args:
        selected_columns (list): The column order of the selected watchlist.
    """
    # Check if the user is logged in
    if "user_email" not in st.session_state:
        st.error("Please log in to view your watchlists.")
        return

    # Initialize database classes
    db_watchlist = dbWatchlist()
    db_tickers_data = dbTickersData()

    # Retrieve all watchlists for the user
    watchlists = db_watchlist.get_watchlists(st.session_state["user_email"])
    all_tickers_data = []

    if watchlists:
        for watchlist in watchlists:
            watchlist_name = watchlist[0]
            tickers = db_watchlist.get_tickers_in_watchlist(st.session_state["user_email"], watchlist_name)
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

            st.markdown("### 📜 All Watchlist Stocks")
            st.dataframe(formatted_df, use_container_width=True)

            # Input for typing a ticker name
            st.markdown("### 🔍 Find a Stock")
            typed_ticker = st.text_input("Type a ticker name:")

            # Dropdown for selecting a ticker (sorted alphabetically)
            st.markdown("### 📈 Select a Stock to Display Chart")
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
                    #tchart.plot_candlestick_chart(50)
                else:
                    st.warning(f"Ticker '{ticker_to_display}' not found in the watchlists.")
        else:
            st.warning("No tickers found in your watchlists.")
    else:
        st.warning("You have no watchlists. Please create one to view stocks.")


def addAIButton(tickersJSON, selectedwatchlist,numberOfWords=50):
    if st.button("Show AI Indication"):
        ms = messaging()
        ms.send("User accessing AI for watchlist " )
        AIModel = myOpenAIv1(model="gpt-4o-mini")
        system_content = f"You are an assistant who  provides financial advices on a watchlist shared in json for a set of stocks.  Indication in {numberOfWords} words."
        user_content = "This is the json containing the indicators for each tickers:"+str(tickersJSON)+".Provide  as output: a general indication on the watchlist and for each stock respectively indicating whether Strong buy, buy, hold, sell or strong sell. Add a short explaination of the indication. The output must be text I can print and not json. Put in style the stocks in buy or strong buy."
        response, usage = AIModel.get_completion_from_messages(system_content, user_content, temperature=0)
        #st.write(response, unsafe_allow_html=True) #tolto poiche` il reload triggera il caricamento direttamente nella pagina
        st.session_state['display_AI'+selectedwatchlist] = response
        st.rerun()
        return response

def page_watchlist():
    # Verifica se l'utente è loggato
    if "user_email" not in st.session_state:
        st.error("Devi effettuare il login prima di accedere a questa pagina.")
        st.stop()

    # Inizializzazione della classe dbWatchlist e dbTickersData
    db_watchlist = dbWatchlist()
    db_tickers_data = dbTickersData()

    # Impostazioni della pagina
    st.title("📊 Watchlists")
    st.markdown(f"<span style='font-size: 13px; color: #6c757d;'>Utente: {st.session_state['user_email']}</span>",
                unsafe_allow_html=True)

    # Sposta i pulsanti nella sidebar
    with st.sidebar:
        user_email = st.session_state.get("user_email", "Utente")
        st.markdown(f"**User: {user_email}**")

        if st.button("Signals"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "signals"}
            st.rerun()

        if st.button("Insights"):
            st.session_state.query_params = {"page": "insights"}
            st.rerun()

        if st.button("Alligator"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "alligator"}
            st.rerun()


        if st.button("Portfolio"):
            st.session_state.query_params = {"page": "portfolio"}
            st.rerun()

        if st.button("Logout"):
            st.session_state.clear()
            st.session_state.query_params = {"page": "login"}
            st.rerun()

    # Recupera le watchlist dell'utente
    watchlists = db_watchlist.get_watchlists(st.session_state["user_email"])

    trovateWatchlists=0
    if watchlists:
        trovateWatchlists = 1
        watchlist_names = [watchlist[0] for watchlist in watchlists]

        selected_watchlist = st.selectbox("Select a Watchlist", watchlist_names, index=0)
        st.markdown(
            f"<span style='font-size:18px; font-weight: bold;'>📈 Ticker nella Watchlist '{selected_watchlist}'</span>",
            unsafe_allow_html=True)

        # Recupera i ticker dalla watchlist e i loro dati dal database
        tickers = [ticker[0] for ticker in
                   db_watchlist.get_tickers_in_watchlist(st.session_state["user_email"], selected_watchlist) if
                   ticker[0]]

        ticker_data = []
        tickers_json=[]
        for ticker_symbol in tickers:
            try:
                ticker_info = db_tickers_data.load_json_data(ticker_symbol)
                tickers_json.append(ticker_info)
                if ticker_info:
                    ticker_data.append([
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
                else:
                    print("No data found for:"+ticker_symbol)
            except Exception as e:
                st.warning(f"Error during download data for  {ticker_symbol}: {e}")

        # Mostra i dati della watchlist selezionata

        if ticker_data:
            columns = ["Ticker", "var%2d", "Scoring", "Signal6", "var%5d", "var%10d","var%30d",'Volume', "ADX",
                       "MACDH", "RSI", "Signal1", "Signal2", "Signal3", "Signal4", "Signal5", "Close",'ticker_name']
            ticker_df = pd.DataFrame(ticker_data, columns=columns)

            ticker_df = ticker_df.sort_values(by="Scoring", ascending=False) #ordina

            # Formattazione per percentuali
            for col in ["var%2d", "var%5d", "var%10d","var%30d"]:
                ticker_df[col] = pd.to_numeric(ticker_df[col], errors='coerce')
                ticker_df[col] = ticker_df[col].map("{:.2f}%".format)

            # Funzione per colorare testo in base al valore positivo o negativo
            def color_positive_negative(val):
                try:
                    val_float = float(str(val).replace('%', ''))
                    return 'color: green' if val_float > 0 else 'color: red'
                except (ValueError, TypeError):
                    return 'color: black'

            #Ordina prima di visualizzare

            st.write("Last processing: " + read_last_line_content_in_brackets())

            styled_df = ticker_df.style.applymap(color_positive_negative,
                                                 subset=["var%2d", "var%5d", "var%10d", "Scoring","var%30d"])
            st.dataframe(styled_df, use_container_width=True)
            ##### Visualizza AI indication e pulsante
            if 'display_AI'+selected_watchlist in st.session_state:
                #if (selected_watchlist==st.session_state['selected_watchlist_for_AI']):
                st.write(st.session_state['display_AI'+selected_watchlist])
            addAIButton(tickers_json, selected_watchlist,180)

            # Selezione del ticker per visualizzare il grafico
            selected_ticker = st.selectbox("Display chart", [""] + list(ticker_df['Ticker']), index=0)
            if selected_ticker:
                st.markdown(f"**Ticker selezionato:** {selected_ticker}")
                tchart = charts(selected_ticker)
                tchart.plot_ticker_price_and_macd()
                #tchart.plot_candlestick_chart(50)

        else:
            st.warning("No tickers available in this watchlist.")
    else:
        st.warning("No watchlist available. Create a new watchlist.")

    selected_columns = ["Ticker", "var%2d", "Scoring","Signal2", "Signal3", "Signal6",  "ADX","var%5d", "var%10d", "var%30d",
                        "Volume", "MACDH", "RSI", "Signal1",
                        "Signal4", "Signal5", "Close", "Ticker Name"]
    display_all_watchlist_stocks(selected_columns)

    # Gestione delle Watchlist
    st.markdown("<span style='font-size:18px; font-weight: bold;'>⚙️ Gestione delle Watchlist</span>",
                unsafe_allow_html=True)


    # Creazione di una nuova watchlist
    with st.expander("➕ Create new watchlist"):
        new_watchlist_name = st.text_input("Watchlist name")
        if st.button("Create watchlist"):
            if new_watchlist_name:
                db_watchlist.create_watchlist(st.session_state["user_email"], new_watchlist_name)
                st.success(f"Watchlist '{new_watchlist_name}' created!")
                st.rerun()
            else:
                st.error("Insert a name for the watchlist.")

    # Eliminazione della watchlist selezionata
    if trovateWatchlists:
        with st.expander("🗑️ Delete selected watchlist"):
            if watchlists:
                if st.button("Delete watchlist"):
                    db_watchlist.delete_watchlist(selected_watchlist, st.session_state["user_email"])
                    st.success(f"Watchlist '{selected_watchlist}' deleted!")
                    st.rerun()

    # Rimozione di un ticker dalla watchlist
    if trovateWatchlists:
        with st.expander("❌ Remove a ticker from a watchlist"):
            if tickers:
                ticker_to_remove = st.selectbox("Select the ticker to delete", tickers)
                if st.button("Delete ticker"):
                    db_watchlist.delete_ticker_from_watchlist(st.session_state["user_email"], selected_watchlist,ticker_to_remove)
                    st.success(f"Ticker {ticker_to_remove} deleted.")
                    st.rerun()

    # Aggiunta di un nuovo ticker alla watchlist
    if trovateWatchlists:
        with st.expander("➕ Add a new ticker to a watchlist"):
            new_ticker_symbol = st.text_input("Ticker (es. AAPL)").upper()
            if st.button("Add ticker"):
                if new_ticker_symbol:
                    dbV=dbValidTickers()
                    tickerExist=dbV.ticker_exists(new_ticker_symbol,"IT","ETF")
                    if not tickerExist:
                        ticker = yf.Ticker(new_ticker_symbol)
                        ticker_info = ticker.info
                        ticker_name = ticker_info['longName']
                        #creo dati analisi tecnica ed aggiungo al db
                        ts = GenerateScoringAndSignals(new_ticker_symbol, ticker_name, ema_period=50, period='2y', candles=0)
                        if len(ts.data) > 10:
                            ts.run()
                            json_data = ts.download_json()
                            # print(json_data)
                            # Aggiorna db che contiene il ticker con i dati aggiornati, anche con nation and instrument_type
                            # print("Salvo")
                            # print(json_data)
                            dbT = dbTickersData()
                            dbT.save_json_data(json_data, "IT", "ETF")
                            dbV.add_ticker(new_ticker_symbol, ticker_name,"IT","ETF")
                        else:
                            print("Ticker with less than 10 days data. Not added")

                    else: #il ticker esiste gia` nel DB
                        print(new_ticker_symbol+" exists in DB, don't add")
                    try:

                        db_watchlist.add_ticker_to_watchlist(selected_watchlist, st.session_state["user_email"],
                                                         new_ticker_symbol)
                        st.success(f"Ticker {new_ticker_symbol} added to the watchlist {selected_watchlist}.")
                        st.rerun()
                    except ValueError as e:
                        st.warning(str(e))  # Mostra l'avviso in caso di ticker duplicato
                    except Exception as e:
                        st.error(f"Error when adding the ticker: {e}")
                else:
                    st.error("Insert a ticker symbol.")

# --- Ticker Search Section ---
    # Input for search keywords

    keywords = st.text_input("Find tickers by name:")
    db_tickers_data = dbTickersData()

    if keywords:
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        search_results_df = db_tickers_data.search_tickers(search_terms=keyword_list)

        if not search_results_df.empty:
            # Display the available columns for debugging
            #st.write("Available columns:", search_results_df.columns.tolist())

            # Convert relevant columns to numeric for formatting
            numeric_columns = [
                'percent_change_2', 'percent_change_5', 'percent_change_10', 'adx',
                'macd_histogram', 'rsi', 'scoring', 'volume', 'close'
            ]
            for col in numeric_columns:
                if col in search_results_df.columns:
                    search_results_df[col] = pd.to_numeric(search_results_df[col], errors='coerce')

            # Rename columns for display
            search_results_df = search_results_df.rename(columns={
                'ticker': 'Ticker',
                'ticker_name': 'Ticker Name',
                'percent_change_2': 'var%2d',
                'percent_change_5': 'var%5d',
                'percent_change_10': 'var%10d',
                'percent_change_30': 'var%30d',
                'volume': 'Volume',
                'adx': 'ADX',
                'macd_histogram': 'MACDH',
                'rsi': 'RSI',
                'signal1': 'Signal1',
                'signal2': 'Signal2',
                'signal3': 'Signal3',
                'signal4': 'Signal4',
                'signal5': 'Signal5',
                'close': 'Close',
                'scoring': 'Scoring',
                'signal6': 'Signal6',

            })
            initial_df=search_results_df

            # Ensure the correct display order for columns
            desired_column_order = [
                "Ticker", "var%2d", "Scoring", "Signal6", "var%5d", "var%10d",'var%30d','Volume',
                "ADX", "MACDH", "RSI", "Signal1", "Signal2", "Signal3", "Signal4", "Signal5", "Close",'Ticker Name'
            ]
            search_results_df = search_results_df[
                [col for col in desired_column_order if col in search_results_df.columns]]

            # Style the DataFrame
            def highlight_text(val):
                return 'color: green' if isinstance(val, (float, int)) and val > 0 else 'color: red'

            search_results_df['Volume'] = search_results_df['Volume'].fillna(0).astype(int)

            for col in ['var%2d', 'var%5d', 'var%10d', 'var%30d']:
                search_results_df[col] = pd.to_numeric(search_results_df[col], errors='coerce')

            styled_df = (
                search_results_df.style
                .applymap(highlight_text, subset=['Scoring', 'var%2d', 'var%5d', 'var%10d','var%30d'])
                .format({
                    'var%2d': "{:+.2f}%",
                    'var%5d': "{:+.2f}%",
                    'var%10d': "{:+.2f}%",
                    'var%30d': "{:+.2f}%",
                    'ADX': "{:.2f}",
                    'MACDH': "{:.2f}",
                    'RSI': "{:.2f}",
                    'Close': "{:,.2f}",
                    'Volume': "{:.0f}"



                }, na_rep="-")
            )

            # Display Ticker Names below the table
            st.write("**Ticker  and Ticker Name founded:**")
            ticker_pairs = "\n".join(
                [f"- {ticker}: {name}" for ticker, name in
                 zip(initial_df['Ticker'], initial_df['Ticker Name'])]
            )
            st.text(ticker_pairs)


            st.dataframe(styled_df, use_container_width=True)



            # Selectbox for viewing ticker chart
            st.write("---")
            ticker_options = [""] + search_results_df['Ticker'].tolist()
            sel_ticker = st.selectbox("Display chart:", ticker_options)

            # Show the selected ticker name and chart
            if sel_ticker:
                ticker_name = search_results_df.loc[search_results_df['Ticker'] == sel_ticker, 'Ticker Name'].values[0]
                st.markdown(f"**Selected ticker name:** {ticker_name}")
                tchart = charts(sel_ticker)
                tchart.plot_ticker_price_and_macd()
                #tchart.plot_candlestick_chart(50)


        else:
            st.warning("Zero results for this search.")






