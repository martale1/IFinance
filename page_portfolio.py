from utils import read_last_line_content_in_brackets, read_last_lines_of_log
import warnings
import streamlit as st
import pandas as pd
from dbPortfolio import dbPortfolio
from Ticker import Ticker
from charts import charts
from dbTickersData import dbTickersData


def portfolio_page():
    # Verifica se l'utente è loggato
    if "user_email" not in st.session_state:
        st.error("Devi effettuare il login prima di accedere a questa pagina.")
        st.stop()

    db_portfolio = dbPortfolio()

    # Impostazioni della pagina
    st.title("💼 Portfolios")
    st.markdown(f"<span style='font-size: 13px; color: #6c757d;'>Utente: {st.session_state['user_email']}</span>", unsafe_allow_html=True)

    # Sposta i pulsanti nella sidebar
    with st.sidebar:


        if st.button("Watchlist"):
            st.session_state.query_params = {"page": "watchlist"}
            st.rerun()

        if st.button("Insights"):
            st.session_state.query_params = {"page": "insights"}
            st.rerun()

        if st.button("Signals"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "signals"}
            st.rerun()

        if st.button("Alligator"):
            if 'display_chart' in st.session_state:
                del st.session_state['display_chart']
            st.session_state.query_params = {"page": "alligator"}
            st.rerun()


        if st.button("Logout"):
            st.session_state.clear()
            st.session_state.query_params = {"page": "login"}
            st.rerun()



    with st.container():
        st.markdown("<span style='font-size:18px; font-weight: bold;'>📂 Select a portfolio</span>", unsafe_allow_html=True)
        portfolios = db_portfolio.get_portfolios(st.session_state["user_email"])

        if portfolios:
            portfolio_names = [portfolio[1] for portfolio in portfolios]
            selected_portfolio = st.selectbox("Select a portfolio", portfolio_names)

            selected_portfolio_id = next(portfolio[0] for portfolio in portfolios if portfolio[1] == selected_portfolio)
            st.markdown(f"<span style='font-size:18px; font-weight: bold;'>📈 Ticker nel portafoglio '{selected_portfolio}'</span>", unsafe_allow_html=True)
            st.write("Last processing: " + read_last_line_content_in_brackets())

            tickers = db_portfolio.get_tickers_in_portfolio(selected_portfolio_id)

            if tickers:
                ticker_data = []

                for ticker_info in tickers:
                    ticker_symbol, quantity, avg_price, _market_price, _change_percentage = ticker_info

                    try:
                        avg_price = float(avg_price)
                    except ValueError:
                        avg_price = 0.0

                    try:
                        market_price = float(_market_price) if _market_price else 0.0
                    except ValueError:
                        market_price = 0.0

                    ticker_instance = Ticker(ticker=ticker_symbol)
                    ticker_instance.generateTickerTAindicatorsScoringandSignals(period='2y')

                    if ticker_instance.close:
                        market_price = float(ticker_instance.close)

                    change_percentage = ((market_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0.0
                    scoring = ticker_instance.scoring
                    signal6 = ticker_instance.signal6
                    p2d=ticker_instance.percent_change_2

                    ticker_data.append([
                        ticker_symbol,p2d, scoring, signal6, f"{change_percentage:+.2f}%", quantity, avg_price, market_price,
                    ])

                columns = ["Ticker","p2d%", "Scoring", "Signal6", "Variazione %", "Quantità", "PCarico", "PMercato"]
                ticker_df = pd.DataFrame(ticker_data, columns=columns)

                ticker_df["Quantità"] = pd.to_numeric(ticker_df["Quantità"], errors='coerce')
                ticker_df["PCarico"] = pd.to_numeric(ticker_df["PCarico"], errors='coerce')
                ticker_df["PMercato"] = pd.to_numeric(ticker_df["PMercato"], errors='coerce')
                ticker_df["Variazione %"] = pd.to_numeric(ticker_df["Variazione %"].str.replace('%', ''), errors='coerce')

                ticker_df["Variazione Assoluta"] = (ticker_df["PMercato"] - ticker_df["PCarico"]) * ticker_df["Quantità"]
                ticker_df["Investimento Totale"] = ticker_df["PCarico"] * ticker_df["Quantità"]

                ticker_df = ticker_df[["Ticker", "p2d%","Variazione %", "Variazione Assoluta", "Scoring", "Signal6", "PMercato", "Quantità", "PCarico", "Investimento Totale"]]

                investimento_totale = ticker_df["Investimento Totale"].sum()
                totale_variazione_assoluta = ticker_df["Variazione Assoluta"].sum()

                variazione_percentuale_totale = (totale_variazione_assoluta / investimento_totale) * 100 if investimento_totale > 0 else 0.0

                def color_text(val):
                    if isinstance(val, str):
                        val = val.replace('%', '')
                    try:
                        val = float(val)
                        color = 'green' if val >= 0 else 'red'
                    except (TypeError, ValueError):
                        color = 'black'
                    return f'color: {color}'

                ticker_df["p2d%"] = pd.to_numeric(ticker_df["p2d%"].str.replace('%', ''), errors='coerce')

                ticker_df["p2d%"] = ticker_df["p2d%"].map("{:+,.2f}%".format)

                ticker_df["Variazione %"] = ticker_df["Variazione %"].map("{:+,.2f}%".format)
                ticker_df["Variazione Assoluta"] = ticker_df["Variazione Assoluta"].map("{:,.2f}".format)
                ticker_df["PCarico"] = ticker_df["PCarico"].map("{:,.4f}".format)
                ticker_df["PMercato"] = ticker_df["PMercato"].map("{:,.4f}".format)
                ticker_df["Investimento Totale"] = ticker_df["Investimento Totale"].map("{:,.2f}".format)
                ticker_df["Quantità"] = ticker_df["Quantità"].map("{:,.0f}".format)

                styled_df = ticker_df.style.applymap(color_text, subset=['p2d%','Variazione %', 'Variazione Assoluta'])
                st.dataframe(styled_df, use_container_width=True)

                st.markdown(f"**Total investement:** {investimento_totale:,.2f} €")
                st.markdown(f"**Current value:** {investimento_totale + totale_variazione_assoluta:,.2f} €")

                variazione_percentuale_color = 'green' if variazione_percentuale_totale >= 0 else 'red'
                variazione_assoluta_color = 'green' if totale_variazione_assoluta >= 0 else 'red'

                st.markdown(
                    f"<span style='font-size: 16px;'>Percentage variation: <span style='color: {variazione_percentuale_color};'>{variazione_percentuale_totale:+,.2f}%</span></span>",
                    unsafe_allow_html=True)
                st.markdown(
                    f"<span style='font-size: 16px;'>Total absolute variation: <span style='color: {variazione_assoluta_color};'>{totale_variazione_assoluta:,.2f} €</span></span>",
                    unsafe_allow_html=True)

                # Sezione grafico dei titoli in portafoglio
                selected_ticker = st.selectbox("Display chart", [""] + list(ticker_df['Ticker']), index=0)
                if selected_ticker:
                    st.markdown(f"**Selected ticker:** {selected_ticker}")
                    tchart = charts(selected_ticker)
                    tchart.plot_ticker_price_and_macd()
                    tchart.plot_candlestick_chart(50)
            else:
                st.warning("No tickers found in this portfolio.")
        else:
            st.warning("No portofolios available. Create a new one to start.")

        st.markdown("<span style='font-size:18px; font-weight: bold;'>⚙️ Portafolio manager</span>", unsafe_allow_html=True)

        with st.expander("➕ Create a new portfolio"):
            new_portfolio_name = st.text_input("Portfolio name")
            if st.button("Create portfolio"):
                if new_portfolio_name:
                    db_portfolio.create_portfolio(st.session_state["user_email"], new_portfolio_name)
                    st.success(f"Portfolio '{new_portfolio_name}' created!")
                    st.rerun()
                else:
                    st.error("Insert portfolio name.")
        if portfolios:

            with st.expander("🗑️ Delete the selected portfolio"):
                if portfolios:
                    if st.button("Delete portfolio"):
                        db_portfolio.delete_portfolio(selected_portfolio_id)
                        st.success(f"Portfolio '{selected_portfolio}' deletec!")
                        st.rerun()

            with st.expander("❌ Remove a ticker from portfolio"):
                if tickers:
                    ticker_to_remove = st.selectbox("Selecte the ticker", ticker_df["Ticker"])
                    if st.button("Remove ticker"):
                        db_portfolio.delete_ticker_from_portfolio(selected_portfolio_id, ticker_to_remove)
                        st.success(f"Ticker {ticker_to_remove} removed.")
                        st.rerun()

            with st.expander("➕ Add a new ticker to portfolio"):
                new_ticker_symbol = st.text_input("Ticker (es. AAPL)")
                new_ticker_quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
                new_ticker_price = st.number_input("Load price (Pc)", min_value=0.0, step=0.01)
                if st.button("Add ticker"):
                    if new_ticker_symbol and new_ticker_quantity and new_ticker_price:
                        try:
                            new_ticker = Ticker(ticker=new_ticker_symbol)
                            new_ticker.generateTickerTAindicatorsScoringandSignals(period='2y')

                            db_portfolio.add_ticker_to_portfolio(selected_portfolio_id, new_ticker, new_ticker_quantity, new_ticker_price)
                            st.success(f"Ticker {new_ticker_symbol} added to  {selected_portfolio}.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Errore when adding the ticker: {e}")
                    else:
                        st.error("Compile all the fields.")


warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
