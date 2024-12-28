
import streamlit as st
import matplotlib.pyplot as plt
from Ticker import Ticker
from dbWatchlist import dbWatchlist  # Assuming you have this class already
from openaimyv1 import myOpenAIv1
from dbTickersData import dbTickersData
from messaging import messaging
import mplfinance as mpf
import pandas as pd

class charts:
    def __init__(self, ticker_symbol, period='2y',buttonAddToWatchlist=0):
        ticker_symbol = ticker_symbol.replace(" ", "")
        self.ticker_symbol = ticker_symbol
        self.period = period
        self.ticker_instance = Ticker(ticker=ticker_symbol)
        self.ticker_instance.generateTickerTAindicatorsScoringandSignals(period=period)
        self.buttonAddToWatchList=buttonAddToWatchlist




    def plot_candlestick_chart(self, days=50):
        """
        Visualizza il grafico a candele per il ticker selezionato, con un numero di giorni specificato.

        Args:
            days (int): Numero di giorni da visualizzare nel grafico a candele.
        """
        data = self.ticker_instance.data  # DataFrame con dati storici, incluso 'Open', 'High', 'Low', 'Close'

        # Filtra per il numero di giorni specificato
        data_filtered = data.tail(days)

        if not {'Open', 'High', 'Low', 'Close', 'Volume'}.issubset(data_filtered.columns):
            st.error(
                "Dati insufficienti per il grafico a candele. Assicurarsi che i dati includano Open, High, Low, Close, e Volume.")
            return

        # Converti l'indice a datetime per mplfinance
        data_filtered.index = pd.to_datetime(data_filtered.index)

        # Configura il grafico a candele
        mpf_style = mpf.make_mpf_style(base_mpf_style='classic', marketcolors=mpf.make_marketcolors(up='g', down='r'))
        fig, ax = mpf.plot(
            data_filtered,
            type='candle',
            volume=True,
            style=mpf_style,
            title=f"Grafico a Candele di {self.ticker_symbol}",
            ylabel="Prezzo",
            ylabel_lower="Volume",
            returnfig=True
        )

        # Mostra il grafico su Streamlit
        st.pyplot(fig)



    def addAIButton(self,ticker,numberOfWords=50):

        if st.button("Show AI Indication for "+ticker):

            myDb = dbTickersData()
            jsonTicker=myDb.load_json_data(ticker)
            print("charts.py: addAIButton")
            print(jsonTicker)
            print("----------------------")
            ms = messaging()
            ms.send("User accessing AI: "+ticker)
            AIModel = myOpenAIv1(model="gpt-4o-mini")
            system_content = (f"You are an assistant who  provides financial advices  based on technical analysis"
                              f" indicators received in input in json format. Indication in {numberOfWords} words."
                              f" The explaination must include the technicald indicators and also the candlestick"
                              f" patterns (if present)")
            user_content = ("Provide  as output: indication with one the values (Strong buy, buy, hold, sell or"
                            " strong sell) along with an analysis of the indicators shared to justify the indication."
                            " My input data are here reported:")+str(jsonTicker)+(". Separate the text of the indication "
                                                                                  "from the technical analysis and candlestick")
            #Analisi piu` accurata con split, usata in vecchia versione
            system_content = f"You are an assistant who  provides financial advices  based on technical analysis indicators received in input. Indication with an explaination in {numberOfWords} words"
            # Json
            user_content = "provide  as output: indication with one the values (Strong buy, buy, hold, sell or strong sell), the explaination, and the  candlestick explaination. The input for the stock is this:" + str(jsonTicker)

            response, usage = AIModel.get_completion_from_messages(system_content, user_content, temperature=0)
            st.write(response, unsafe_allow_html=True)

            #system_content ="you are an assistant that is retrieving latest financial news on a ticker"
            #user_content="Find the 2 latest news on Tesla  or the domain the ticker is investing. Provide   a formatted output with the date of the news, the title, the summary, the url"
            #response, usage = AIModel.get_completion_from_messages(system_content, user_content, temperature=0)
            #st.write(response, unsafe_allow_html=True)

    def format_indicators(self, sl, adx, dxp, dxm, rsi, macdh, sk, sd):
        # Tenta di convertire i parametri in float, se possibile
        try:
            adx = float(adx)
            dxp = float(dxp)
            dxm = float(dxm)
            rsi = float(rsi)
            macdh = float(macdh)
            sk = float(sk)
            sd = float(sd)
        except ValueError:
            return "Errore: I valori degli indicatori devono essere numerici."

        # Determine the color for adx, dxp, and dxm based on the rules
        if adx > 25:
            if dxp > dxm:
                adx_color = 'green'
                dxp_color = 'green'
                dxm_color = 'green'
            else:
                adx_color = 'red'
                dxp_color = 'red'
                dxm_color = 'red'
        else:
            # Default color when adx <= 25
            adx_color = 'black'
            dxp_color = 'black'
            dxm_color = 'black'

        # Determine the color for rsi
        rsi_color = 'green' if rsi >= 50 else 'red'

        # Determine the color for macdh
        macdh_color = 'green' if macdh > 0 else 'red'

        # Determine the color for sk and sd
        if sk > 70 and sd > 70:
            if sk > sd:
                sk_color = 'green'
                sd_color = 'green'
            else:
                sk_color = 'orange'
                sd_color = 'orange'
        elif sk < 30 and sd < 30:
            if sk < sd:
                sk_color = 'red'
                sd_color = 'red'
            else:
                sk_color = 'orange'
                sd_color = 'orange'
        else:
            sk_color = 'black'
            sd_color = 'black'

        # Formatta la stringa di output con i valori e i colori associati
        return f"""
        ADX: <span style='color:{adx_color};'>{adx}</span>, 
        DX+: <span style='color:{dxp_color};'>{dxp}</span>, 
        DX-: <span style='color:{dxm_color};'>{dxm}</span>, 
        RSI: <span style='color:{rsi_color};'>{rsi}</span>, 
        MACDH: <span style='color:{macdh_color};'>{macdh}</span>, 
        SK: <span style='color:{sk_color};'>{sk}</span>, 
        SD: <span style='color:{sd_color};'>{sd}</span>
        """

    def color_scoring(self, value):
        try:
            value = int(value)
        except ValueError:
            return f'<span style="color:red;">Invalid value</span>'

        if value == 4:
            color = 'green'
        elif value == 3:
            color = 'green'
        elif value in [0, 1, 2]:
            color = 'orange'
        else:
            color = 'red'

        return f'<span style="color:{color};">{value}</span>'

    def color_percentage(self, value):
        try:
            value = float(value)
        except (ValueError, TypeError):
            return f'<span style="color:red;">Invalid value</span>'

        color = 'green' if value > 0 else 'red'
        return f'<span style="color:{color};">{value:.2f}%</span>'

    def addWatchlistButton(self):
        db_watchlist = dbWatchlist()
        watchlists = db_watchlist.get_watchlists(st.session_state["user_email"])
        print(watchlists)
        if watchlists:
            watchlist_names = [""]+[watchlist[0] for watchlist in watchlists]

            selected_wl=st.selectbox("Inserisci ticker in watchlist", watchlist_names, index=0)
            if selected_wl:
                st.write("Inserisco item in "+selected_wl)


    def plot_ticker_price_and_macd(self):
        ticker_instance = self.ticker_instance
        scoring_color = self.color_scoring(ticker_instance.scoring)
        signalS6String = ticker_instance.signal6
        close_value = ticker_instance.close
        sl = ticker_instance.atr_trailing_stop_loss
        v = ticker_instance.volume

        percent_change_2_colored = self.color_percentage(float(ticker_instance.percent_change_2 or 0))
        percent_change_5_colored = self.color_percentage(float(ticker_instance.percent_change_5 or 0))
        percent_change_10_colored = self.color_percentage(float(ticker_instance.percent_change_10 or 0))
        percent_change_30_colored = self.color_percentage(float(ticker_instance.percent_change_30 or 0))
        ticker_name = ticker_instance.ticker_name

        adx = ticker_instance.adx
        dxp = ticker_instance.dx_plus
        dxm = ticker_instance.dx_minus
        rsi = ticker_instance.rsi
        macdh = ticker_instance.macd_histogram
        sk = ticker_instance.stochastic_k
        sd = ticker_instance.stochastic_d

        try:
            close_value = float(close_value)
            sl = float(sl)

            take_profit = round(close_value + (close_value - sl), 2)
            slpercent = round((close_value - sl) / sl * 100, 2)

        except ValueError:
            st.error("Errore nella conversione dei valori di Close o SL in numeri.")

        st.markdown(f"<h1 style='font-size:16px;'>{ticker_name}</h1>", unsafe_allow_html=True)
        st.markdown(f"Scoring: {scoring_color} | {signalS6String}", unsafe_allow_html=True)
        st.write(f"Volume:{v}")
        st.write(f"Close:{close_value} | SL:{sl} | TP:{take_profit} | var%:{slpercent}%")
        st.write(
            f"2d:{percent_change_2_colored} | 5d:{percent_change_5_colored} | 10d:{percent_change_10_colored} 30d:{percent_change_30_colored} V:{v}",
            unsafe_allow_html=True)
        formatted_indicators = self.format_indicators(sl, adx, dxp, dxm, rsi, macdh, sk, sd)
        st.write(formatted_indicators, unsafe_allow_html=True)
        #Url sito yahoo
        url = f"https://it.finance.yahoo.com/quote/{ticker_instance.ticker}"
        st.markdown(f"[{ticker_instance.ticker} {ticker_instance.ticker_name}]({url})", unsafe_allow_html=True)

        if hasattr(ticker_instance, 'data') and 'Close' in ticker_instance.data.columns:
            data = ticker_instance.data
            num_days = st.slider(f"Seleziona il numero di giorni da visualizzare per {ticker_instance.ticker}", min_value=10, max_value=len(data),
                                 value=50)
            data_filtered = data.tail(num_days)
            self.plot_graphs(data_filtered)
            self.addAIButton(ticker_instance.ticker,100)
            if self.buttonAddToWatchList:
                self.addWatchlistButton()



    def plot_graphs(self, data_filtered):
        close_data = data_filtered['Close']
        atr_trailing_stop_loss_data = data_filtered.get('ATR_Trailing_Stop_Loss')
        macd_data = data_filtered.get('MACD')
        macd_signal_data = data_filtered.get('MACD_Signal')
        macd_histogram_data = data_filtered.get('MACD_Histogram')
        rsi_data = data_filtered.get('RSI')
        stochastic_k_data = data_filtered.get('Stochastic_K')
        stochastic_d_data = data_filtered.get('Stochastic_D')

        indicators = {
            "Alligator Jaw": data_filtered.get('Alligator_Jaw'),
            "Alligator Teeth": data_filtered.get('Alligator_Teeth'),
            "Alligator Lips": data_filtered.get('Alligator_Lips'),
            "Bollinger Upper": data_filtered.get('Bollinger_Upper'),
            "Bollinger Middle": data_filtered.get('Bollinger_Middle'),
            "Bollinger Lower": data_filtered.get('Bollinger_Lower'),
        }

        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(12, 15), sharex=True)

        ax1.plot(close_data.index, close_data.values, label=f"{self.ticker_symbol} Price", color='black', linestyle='-')
        ax1.scatter(close_data.index, close_data.values, color='black', marker='o')

        if atr_trailing_stop_loss_data is not None:
            last_atr_trailing_stop_loss = atr_trailing_stop_loss_data.iloc[-1]
            last_close = close_data.iloc[-1]
            take_profit = last_close + (last_close - last_atr_trailing_stop_loss)

            ax1.axhline(last_atr_trailing_stop_loss, color='red', linestyle='--', linewidth=1,
                        label=f"SL: {last_atr_trailing_stop_loss:.2f}€)")
            ax1.axhline(take_profit, color='green', linestyle='--', linewidth=1, label=f"TP: {take_profit:.2f}€")

        if indicators["Alligator Jaw"] is not None:
            ax1.plot(indicators["Alligator Jaw"].index, indicators["Alligator Jaw"].values, label="Alligator Jaw",
                     color='blue')
        if indicators["Alligator Teeth"] is not None:
            ax1.plot(indicators["Alligator Teeth"].index, indicators["Alligator Teeth"].values, label="Alligator Teeth",
                     color='red')
        if indicators["Alligator Lips"] is not None:
            ax1.plot(indicators["Alligator Lips"].index, indicators["Alligator Lips"].values, label="Alligator Lips",
                     color='green')

        for label, indicator in indicators.items():
            if indicator is not None and "Alligator" not in label:
                ax1.plot(indicator.index, indicator.values, linewidth=1, label=label, linestyle='--')

        ax1.set_title(f"Prezzo di Chiusura e Indicatori Tecnici per {self.ticker_symbol}")
        ax1.set_ylabel("Prezzo (€)")
#        ax1.legend()
        ax1.legend(loc="lower left")  # Position the legend at the bottom-left

        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

        if macd_data is not None and macd_signal_data is not None and macd_histogram_data is not None:
            ax2.plot(macd_data.index, macd_data.values, label="MACD", color='blue', linestyle='-')
            ax2.plot(macd_signal_data.index, macd_signal_data.values, label="MACD Signal", color='red', linestyle='-')
            ax2.bar(macd_histogram_data.index, macd_histogram_data.values, color='green', label="MACD Histogram",
                    width=1.5)

            ax2.set_title(f"Indicatori MACD")
            ax2.set_ylabel("Valore MACD")
            ax2.legend()
            ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
        else:
            ax2.text(0.5, 0.5, 'Dati MACD non disponibili', horizontalalignment='center',
                     verticalalignment='center', transform=ax2.transAxes, fontsize=12, color='red')

        if rsi_data is not None and stochastic_k_data is not None and stochastic_d_data is not None:
            ax3.plot(rsi_data.index, rsi_data.values, label="RSI", color='orange', linestyle='-')
            ax3.plot(stochastic_k_data.index, stochastic_k_data.values, label="Stochastic %K", color='blue',
                     linestyle='-')
            ax3.plot(stochastic_d_data.index, stochastic_d_data.values, label="Stochastic %D", color='red',
                     linestyle='-')

            ax3.axhline(80, color='gray', linestyle='--', linewidth=1, label='Overbought (80)')
            ax3.axhline(20, color='gray', linestyle='--', linewidth=1, label='Oversold (20)')
            ax3.axhline(50, color='purple', linestyle='--', linewidth=1, label='Neutral (50)')

            ax3.set_title(f"Indicatori RSI e Stochastic")
            ax3.set_ylabel("Valore RSI/Stochastic")
            ax3.legend()
            ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
        else:
            ax3.text(0.5, 0.5, 'Dati RSI/Stochastic non disponibili', horizontalalignment='center',
                     verticalalignment='center', transform=ax3.transAxes, fontsize=12, color='red')

        plt.tight_layout()
        st.pyplot(fig)
