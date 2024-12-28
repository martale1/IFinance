import streamlit as st
import pandas as pd
from dbTickersDataOLD2 import dbTickersData
from charts import charts


def page_alligator():
    # Initialize database instance
    myDb = dbTickersData()

    # Sidebar for controls and navigation
    with st.sidebar:
        user_email = st.session_state.get("user_email", "User")
        st.markdown(f"**User: {user_email}**")

        nation = st.selectbox("Select the nation", options=["IT"], index=0)
        instrument_type = st.selectbox("Instrument type", options=["ETC", "ETF", "MIB30"], index=0)

        n_value = st.text_input("Number of tickers to visualize:", value="300")
        n_value = int(n_value) if n_value.isdigit() else 10

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

    st.title("Stock Insights - Alligator Page")

    # Retrieve data using get_sorted_tickers_by_signal6
    sorted_tickers = myDb.get_sorted_tickers_by_signal6(
        nation=nation,
        instrument_type=instrument_type,
        secondary_key="scoring",
        additional_columns=[
            "Percent_Change_2", "Percent_Change_5", "Percent_Change_10", "Percent_Change_30",
            "Signal2", "Signal3", "Signal5", "Volume", "adx", "Signal1", "Signal4", "stochastic_k", "RSI", "ticker_name"
        ]
    )

    if not sorted_tickers.empty:
        exclude_columns = ["Ticker", "Signal6", "ticker_name"]
        for col in sorted_tickers.columns:
            if col not in exclude_columns:
                sorted_tickers[col] = pd.to_numeric(sorted_tickers[col], errors='coerce')

        signal6_classes = ["All", "Segnali > 0"] + sorted_tickers['Signal6'].unique().tolist()
        selected_signal6 = st.selectbox("Select signal6 class", options=signal6_classes)

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

        # Limit the number of results
        sorted_tickers_limited = sorted_tickers.head(n_value)

        # Rename columns for display
        column_mapping = {
            "Percent_Change_2": "p2d%",
            "Percent_Change_5": "p5d%",
            "Percent_Change_10": "p10d%",
            "Percent_Change_30": "p30d%",
            "Signal2": "s2",
            "Signal3": "s3",
            "Signal5": "s5",
            "Volume": "V",
            "adx": "adx",
            "Signal1": "s1",
            "Signal4": "s4",
            "stochastic_k": "sk",
            "RSI": "RSI",
            "ticker_name": "ticker_name"
        }
        sorted_tickers_limited = sorted_tickers_limited.rename(columns=column_mapping)

        # Function to apply color styling
        def highlight_percent_change(val):
            try:
                val = float(val)
                color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                return f'color: {color}'
            except ValueError:
                return ''

        # Apply style to the table
        styled_tickers = sorted_tickers_limited.style.applymap(
            highlight_percent_change, subset=["p2d%", "p5d%", "p10d%", "p30d%"]
        ).format({
            "p2d%": "{:.2f}%",
            "p5d%": "{:.2f}%",
            "p10d%": "{:.2f}%",
            "p30d%": "{:.2f}%",
            "adx": "{:.2f}",
            "RSI": "{:.2f}",
            "sk": "{:.2f}",
            "V": "{:,.0f}"
        })

        st.subheader(f"Ordered tickers ({nation} - {instrument_type} - Class: {selected_signal6})")
        st.dataframe(styled_tickers, use_container_width=True)

        # Sort tickers alphabetically for the selectbox
        tickers_sorted = sorted(sorted_tickers_limited['Ticker'].dropna().unique())
        sel_ticker = st.selectbox("Select the ticker to plot", [""] + tickers_sorted)
        if sel_ticker:
            st.markdown(f"**Chart for the selected ticker: {sel_ticker}**")
            tchart = charts(sel_ticker)
            tchart.plot_ticker_price_and_macd()
            #tchart.plot_candlestick_chart(50)

    else:
        st.warning("No results.")

    if not sorted_tickers.empty:
        st.divider()

        signal6_counts = sorted_tickers['Signal6'].value_counts().reset_index()
        signal6_counts.columns = ['Signal6', 'Count']
        total_count = signal6_counts['Count'].sum()
        signal6_counts['Percentage'] = (signal6_counts['Count'] / total_count) * 100

        st.subheader(f"Tickers distributions by signal6 ({nation} - {instrument_type})")
        st.dataframe(signal6_counts)

        st.text(f"Total: {total_count}")

    myDb.close()


if __name__ == "__main__":
    page_alligator()
