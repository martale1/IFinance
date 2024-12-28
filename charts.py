import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from Ticker import Ticker
from dbWatchlist import dbWatchlist
from openaimyv1 import myOpenAIv1
from dbTickersData import dbTickersData
from messaging import messaging
import mplfinance as mpf
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates  # Per formattare le date se necessario

# Imposta uno stile Seaborn uniforme
sns.set_style('darkgrid')  # Utilizza uno stile Seaborn

class charts:
    def __init__(self, ticker_symbol, period='2y', buttonAddToWatchlist=False):
        self.ticker_symbol = ticker_symbol.replace(" ", "")
        self.period = period
        self.ticker_instance = Ticker(ticker=self.ticker_symbol)
        self.ticker_instance.generateTickerTAindicatorsScoringandSignals(period=period)
        self.buttonAddToWatchList = buttonAddToWatchlist  # Consistente con la nomenclatura



    def plot_candlestick_chart(self, days=10):
        data = self.ticker_instance.data

        # Filtra i dati per i giorni specificati
        data_filtered = data.tail(days).copy()

        # Verifica la presenza delle colonne necessarie
        required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
        if not required_columns.issubset(data_filtered.columns):
            st.error("Dati insufficienti per il grafico a candele. Assicurati che i dati includano Open, High, Low, Close e Volume.")
            return

        # Converti l'indice a datetime
        data_filtered.index = pd.to_datetime(data_filtered.index)

        # Definisci uno stile personalizzato per mplfinance
        mpf_style = mpf.make_mpf_style(
            base_mpf_style='yahoo',  # Stile base più moderno
            marketcolors=mpf.make_marketcolors(
                up='green',
                down='red',
                edge='inherit',
                wick='inherit',
                volume='inherit',
                alpha=0.9
            ),
            rc={
                'figure.facecolor': '#f5f5f5',
                'axes.facecolor': '#ffffff',
                'axes.edgecolor': '#cccccc',
                'axes.labelcolor': '#333333'
            }
        )

        # Configura il grafico a candele
        fig, axlist = mpf.plot(
            data_filtered,
            type='candle',
            volume=True,
            style=mpf_style,
            figsize=(12, 8),
            title=f"📈 Grafico a Candele di {self.ticker_symbol}",
            ylabel="Prezzo (€)",
            ylabel_lower="Volume",
            returnfig=True
        )

        # Mostra il grafico in Streamlit
        st.pyplot(fig)

    def addAIButton(self, ticker, numberOfWords=50):
        if st.button(f"🤖 Mostra Indicazioni AI per {ticker}"):
            myDb = dbTickersData()
            jsonTicker = myDb.load_json_data(ticker)
            ms = messaging()
            ms.send(f"User accessing AI: {ticker}")
            AIModel = myOpenAIv1(model="gpt-4o-mini")

            # Prompt per il modello AI
            system_content = (
                f"You are an assistant who provides financial advice based on technical analysis indicators. "
                f"Provide an indication with an explanation in {numberOfWords} words."
            )
            user_content = (
                "Provide as output: an indication with one of the values (Strong Buy, Buy, Hold, Sell, Strong Sell), "
                "the explanation, and the candlestick explanation. The input for the stock is this:\n" + str(jsonTicker)
            )

            response, usage = AIModel.get_completion_from_messages(
                system_content, user_content, temperature=0
            )
            st.success(response)

    def format_indicators(self, sl, adx, dxp, dxm, rsi, macdh, sk, sd):
        try:
            adx = float(adx)
            dxp = float(dxp)
            dxm = float(dxm)
            rsi = float(rsi)
            macdh = float(macdh)
            sk = float(sk)
            sd = float(sd)
        except ValueError:
            return "⚠️ Errore: I valori degli indicatori devono essere numerici."

        # Regole per i colori degli indicatori
        adx_color = 'green' if adx > 25 and dxp > dxm else 'red' if adx > 25 else 'black'
        dxp_color = adx_color
        dxm_color = adx_color
        rsi_color = 'green' if rsi >= 50 else 'red'
        macdh_color = 'green' if macdh > 0 else 'red'

        if sk > 70 and sd > 70:
            sk_color = sd_color = 'green' if sk > sd else 'orange'
        elif sk < 30 and sd < 30:
            sk_color = sd_color = 'red' if sk < sd else 'orange'
        else:
            sk_color = sd_color = 'black'

        return f"""
        **ADX:** <span style='color:{adx_color};'>{adx}</span>, 
        **DX+:** <span style='color:{dxp_color};'>{dxp}</span>, 
        **DX-:** <span style='color:{dxm_color};'>{dxm}</span>, 
        **RSI:** <span style='color:{rsi_color};'>{rsi}</span>, 
        **MACDH:** <span style='color:{macdh_color};'>{macdh}</span>, 
        **SK:** <span style='color:{sk_color};'>{sk:.2f}</span>, 
        **SD:** <span style='color:{sd_color};'>{sd:.2f}</span>
        """

    def color_scoring(self, value):
        try:
            value = int(value)
        except ValueError:
            return "<span style='color:red;'>Valore non valido</span>"

        color = 'green' if value >= 3 else 'orange' if value in [0, 1, 2] else 'red'
        return f"<span style='color:{color};'>{value}</span>"

    def color_percentage(self, value):
        try:
            value = float(value)
        except (ValueError, TypeError):
            return "<span style='color:red;'>Valore non valido</span>"

        color = 'green' if value > 0 else 'red'
        return f"<span style='color:{color};'>{value:.2f}%</span>"

    def addWatchlistButton(self):
        db_watchlist = dbWatchlist()
        watchlists = db_watchlist.get_watchlists(st.session_state.get("user_email", ""))
        if watchlists:
            watchlist_names = [wl[0] for wl in watchlists]
            selected_wl = st.selectbox("Aggiungi ticker a una watchlist (not implemented)", watchlist_names)
            if st.button("📥 Aggiungi"):
                # Implementa la logica per aggiungere il ticker alla watchlist selezionata
                st.success(f"{self.ticker_symbol} è stato aggiunto a {selected_wl}!")

    def plot_ticker_price_and_macd(self):
        ti = self.ticker_instance
        scoring_color = self.color_scoring(ti.scoring)
        signalS6String = ti.signal6
        close_value = ti.close
        sl = ti.atr_trailing_stop_loss
        v = ti.volume

        # Percentuali colorate
        percent_changes = {
            '2d': self.color_percentage(ti.percent_change_2 or 0),
            '5d': self.color_percentage(ti.percent_change_5 or 0),
            '10d': self.color_percentage(ti.percent_change_10 or 0),
            '30d': self.color_percentage(ti.percent_change_30 or 0),
        }

        ticker_name = ti.ticker_name
        adx, dxp, dxm = ti.adx, ti.dx_plus, ti.dx_minus
        rsi, macdh = ti.rsi, ti.macd_histogram
        sk, sd = ti.stochastic_k, ti.stochastic_d

        try:
            close_value = float(close_value)
            sl = float(sl)
            take_profit = round(close_value + (close_value - sl), 2)
            slpercent = round((close_value - sl) / sl * 100, 2)
        except ValueError:
            st.error("⚠️ Errore nella conversione dei valori di Close o SL in numeri.")

        # Intestazioni e informazioni principali
        st.markdown(f"## {ticker_name} ({self.ticker_symbol})")
        st.markdown(f"**Scoring:** {scoring_color} | **Segnale:** {signalS6String}", unsafe_allow_html=True)
        st.markdown(f"**Volume:** {v}")
        st.markdown(f"**Close:** €{close_value:.2f} | **SL:** €{sl:.2f} | **TP:** €{take_profit} | **Var%:** {slpercent}%")
        st.markdown(
            f"**2d:** {percent_changes['2d']} | **5d:** {percent_changes['5d']} | "
            f"**10d:** {percent_changes['10d']} | **30d:** {percent_changes['30d']} | **V:** {v}",
            unsafe_allow_html=True
        )
        formatted_indicators = self.format_indicators(sl, adx, dxp, dxm, rsi, macdh, sk, sd)
        st.markdown(formatted_indicators, unsafe_allow_html=True)

        # Link a Yahoo Finance
        url = f"https://it.finance.yahoo.com/quote/{ti.ticker}"
        st.markdown(f"[Visualizza su Yahoo Finance]({url}) 🔗", unsafe_allow_html=True)

        # Grafici e interazioni
        if hasattr(ti, 'data') and 'Close' in ti.data.columns:
            data = ti.data
            num_days = st.slider(
                f"📅 Seleziona il numero di giorni da visualizzare per {ti.ticker}",
                min_value=20,  # Imposta il minimo a 20 per la MA20
                max_value=len(data),
                value=50
            )
            data_filtered = data.tail(num_days).copy()

            # Assicurati che l'indice sia di tipo DatetimeIndex
            if not isinstance(data_filtered.index, pd.DatetimeIndex):
                data_filtered.index = pd.to_datetime(data_filtered.index)

            # Ordina i dati per data
            data_filtered = data_filtered.sort_index()

            # Filtra i dati per includere solo i giorni lavorativi
            data_filtered = data_filtered[data_filtered.index.dayofweek < 5]

            # Rimuovi eventuali righe con valori NaN negli indicatori
            data_filtered = data_filtered.dropna(subset=['MACD', 'RSI', 'Stochastic_K', 'Stochastic_D'])

            self.addAIButton(ti.ticker, 100)
            self.plot_graphs(data_filtered)

            if self.buttonAddToWatchList:
                self.addWatchlistButton()

    def plot_graphsold(self, data_filtered):
        close_data = data_filtered['Close']
        high_data = data_filtered['High']
        low_data = data_filtered['Low']
        volume_data = data_filtered['Volume']
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

        # Calcola MFI (Money Flow Index)
        typical_price = (high_data + low_data + close_data) / 3
        raw_money_flow = typical_price * volume_data
        data_filtered['Money Flow Positive'] = np.where(typical_price > typical_price.shift(1), raw_money_flow, 0)
        data_filtered['Money Flow Negative'] = np.where(typical_price < typical_price.shift(1), raw_money_flow, 0)
        money_flow_positive = data_filtered['Money Flow Positive'].rolling(window=14).sum()
        money_flow_negative = data_filtered['Money Flow Negative'].rolling(window=14).sum()

        mfi = 100 - (100 / (1 + (money_flow_positive / money_flow_negative)))
        data_filtered['MFI'] = mfi

        # Calcola la media mobile dei volumi a 20 giorni
        data_filtered['Volume_MA20'] = volume_data.rolling(window=20).mean()
        volume_ma20 = data_filtered['Volume_MA20']

        # Calcola l'On Balance Volume (OBV)
        data_filtered['OBV'] = np.where(
            close_data > close_data.shift(1),
            volume_data,
            np.where(
                close_data < close_data.shift(1),
                -volume_data,
                0
            )
        ).cumsum()
        obv_data = data_filtered['OBV']

        # Crea una figura con 5 subplot
        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=5, ncols=1, figsize=(14, 24), sharex=True)

        # Genera un indice numerico continuo
        x = range(len(data_filtered))

        # AX1: Prezzo e Indicatori
        ax1.plot(x, close_data.values, label=f"{self.ticker_symbol} Price", color='#1f77b4', linewidth=1.5)
        ax1.scatter(x, close_data.values, color='#1f77b4', marker='o', s=10)

        if atr_trailing_stop_loss_data is not None:
            last_atr_sl = atr_trailing_stop_loss_data.iloc[-1]
            last_close = close_data.iloc[-1]
            take_profit = last_close + (last_close - last_atr_sl)
            ax1.axhline(last_atr_sl, color='red', linestyle='--', linewidth=1, label=f"SL: €{last_atr_sl:.2f}")
            ax1.axhline(take_profit, color='green', linestyle='--', linewidth=1, label=f"TP: €{take_profit:.2f}")

        # AX2: MACD
        if macd_data is not None and macd_signal_data is not None and macd_histogram_data is not None:
            ax2.plot(x, macd_data.values, label="MACD", color='blue', linewidth=1)
            ax2.plot(x, macd_signal_data.values, label="MACD Signal", color='red', linewidth=1)
            ax2.bar(x, macd_histogram_data.values, color='green', label="MACD Histogram", width=0.8)
            ax2.set_title("📈 Indicatori MACD")
            ax2.legend(loc="upper left", fontsize='small')
            ax2.grid(True, linestyle='--', alpha=0.5)

        # AX3: RSI e Stochastic
        if rsi_data is not None and stochastic_k_data is not None and stochastic_d_data is not None:
            ax3.plot(x, rsi_data.values, label="RSI", color='orange', linewidth=1)
            ax3.plot(x, stochastic_k_data.values, label="SK", color='blue', linewidth=1)
            ax3.plot(x, stochastic_d_data.values, label="SD", color='red', linewidth=1)
            ax3.set_title("📉 Indicatori RSI e Stochastic")
            ax3.legend(loc="upper left", fontsize='small')
            ax3.grid(True, linestyle='--', alpha=0.5)

        # AX4: Volume e Media Mobile
        ax4.bar(x, volume_data.values, color='lightgray', label='Volume')
        ax4.plot(x, volume_ma20.values, label='Volume MA20', color='blue', linewidth=1.5)
        ax4.set_title("📊 Volume e Media Mobile dei Volumi")
        ax4.legend(loc="upper left", fontsize='small')
        ax4.grid(True, linestyle='--', alpha=0.5)

        # AX5: Money Flow Index (MFI)
        ax5.plot(x, mfi.values, label='MFI', color='purple', linewidth=1.5)
        ax5.axhline(80, color='red', linestyle='--', linewidth=0.8, label='Overbought (80)')
        ax5.axhline(20, color='green', linestyle='--', linewidth=0.8, label='Oversold (20)')
        ax5.set_title("📈 Money Flow Index (MFI)")
        ax5.set_ylabel("MFI")
        ax5.legend(loc="upper left", fontsize='small')
        ax5.grid(True, linestyle='--', alpha=0.5)

        # Impostazioni finali del layout
        plt.tight_layout()
        st.pyplot(fig)

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

        # Calcola la media mobile dei volumi a 20 giorni
        data_filtered['Volume_MA20'] = data_filtered['Volume'].rolling(window=20).mean()
        volume_ma20 = data_filtered['Volume_MA20']

        # Calcola l'On Balance Volume (OBV)
        data_filtered['OBV'] = np.where(
            data_filtered['Close'] > data_filtered['Close'].shift(1),
            data_filtered['Volume'],
            np.where(
                data_filtered['Close'] < data_filtered['Close'].shift(1),
                -data_filtered['Volume'],
                0
            )
        ).cumsum()
        obv_data = data_filtered['OBV']

        # Crea una figura con 4 subplot
        fig, (ax1, ax2, ax3, ax4,ax5) = plt.subplots(nrows=5, ncols=1, figsize=(14, 20), sharex=True)

        # Genera un indice numerico continuo
        x = range(len(data_filtered))

        # AX1: Prezzo e Indicatori
        ax1.plot(x, close_data.values, label=f"{self.ticker_symbol} Price", color='#1f77b4', linewidth=1.5)
        ax1.scatter(x, close_data.values, color='#1f77b4', marker='o', s=10)

        if atr_trailing_stop_loss_data is not None:
            last_atr_sl = atr_trailing_stop_loss_data.iloc[-1]
            last_close = close_data.iloc[-1]
            take_profit = last_close + (last_close - last_atr_sl)
            ax1.axhline(last_atr_sl, color='red', linestyle='--', linewidth=1, label=f"SL: €{last_atr_sl:.2f}")
            ax1.axhline(take_profit, color='green', linestyle='--', linewidth=1, label=f"TP: €{take_profit:.2f}")

        # Alligator Indicators
        for label, color in zip(["Alligator Jaw", "Alligator Teeth", "Alligator Lips"], ['blue', 'red', 'green']):
            if indicators[label] is not None:
                ax1.plot(x, indicators[label].values, label=label, color=color, linewidth=1)

        # Bollinger Bands
        for label in ["Bollinger Upper", "Bollinger Middle", "Bollinger Lower"]:
            if indicators[label] is not None:
                ax1.plot(x, indicators[label].values, label=label, linestyle='--', linewidth=1, alpha=0.7)

        ax1.set_title("📊 Prezzo di Chiusura e Indicatori Tecnici")
        ax1.set_ylabel("Prezzo (€)")
        ax1.legend(loc="upper left", fontsize='small')
        ax1.grid(True, linestyle='--', alpha=0.5)

        # AX2: MACD
        if macd_data is not None and macd_signal_data is not None and macd_histogram_data is not None:
            ax2.plot(x, macd_data.values, label="MACD", color='blue', linewidth=1)
            ax2.plot(x, macd_signal_data.values, label="MACD Signal", color='red', linewidth=1)
            ax2.bar(x, macd_histogram_data.values, color='green', label="MACD Histogram", width=0.8)

            ax2.set_title("📈 Indicatori MACD")
            ax2.set_ylabel("Valore MACD")
            ax2.legend(loc="upper left", fontsize='small')
            ax2.grid(True, linestyle='--', alpha=0.5)
        else:
            ax2.text(0.5, 0.5, '⚠️ Dati MACD non disponibili', ha='center', va='center', fontsize=12, color='red')

        # AX3: RSI e Stochastic
        if rsi_data is not None and stochastic_k_data is not None and stochastic_d_data is not None:
            ax3.plot(x, rsi_data.values, label="RSI", color='orange', linewidth=1)
            ax3.plot(x, stochastic_k_data.values, label="SK", color='blue', linewidth=1)
            ax3.plot(x, stochastic_d_data.values, label="SD", color='red', linewidth=1)

            # Linee di riferimento
            for y in [80, 50, 20]:
                color = 'gray' if y == 50 else 'darkgray'
                linestyle = '--'
                ax3.axhline(y, color=color, linestyle=linestyle, linewidth=0.8)

            ax3.set_title("📉 Indicatori RSI e Stochastic")
            ax3.set_ylabel("Valore")
            ax3.legend(loc="upper left", fontsize='small')
            ax3.grid(True, linestyle='--', alpha=0.5)
        else:
            ax3.text(0.5, 0.5, '⚠️ Dati RSI/Stochastic non disponibili', ha='center', va='center', fontsize=12, color='red')

        # AX4: Volume e Media Mobile dei Volumi a 20 Giorni
        volume_data = data_filtered['Volume']
        ax4.bar(x, volume_data.values, color='lightgray', label='Volume')
        ax4.plot(x, volume_ma20.values, label='Volume MA20', color='blue', linewidth=1.5)
        ax4.set_title("📊 Volume e Media Mobile dei Volumi a 20 Giorni")
        ax4.set_ylabel("Volume")
        ax4.legend(loc="upper left", fontsize='small')
        ax4.grid(True, linestyle='--', alpha=0.5)

        # Etichette personalizzate sull'asse X (opzionale)
        ax4.set_xticks(x[::max(1, len(x)//10)])  # Mostra circa 10 etichette
        ax4.set_xticklabels([data_filtered.index[i].strftime('%Y-%m-%d') for i in ax4.get_xticks()], rotation=45, ha='right')

        # AX5: Money Flow Index (MFI)
        mfi_data = data_filtered['MFI']
        ax5.plot(x, mfi_data.values, label='MFI', color='purple', linewidth=1.5)
        ax5.axhline(80, color='red', linestyle='--', label='Ipercomprato (80)')
        ax5.axhline(20, color='green', linestyle='--', label='Ipervenduto (20)')
        ax5.fill_between(x, mfi_data.values, 80, where=(mfi_data.values >= 80), color='red', alpha=0.3)
        ax5.fill_between(x, mfi_data.values, 20, where=(mfi_data.values <= 20), color='green', alpha=0.3)

        # Titolo, etichette e griglia
        ax5.set_title("📈 Money Flow Index (MFI)")
        ax5.set_ylabel("MFI")
        ax5.set_xlabel("Data")
        ax5.legend(loc="upper left", fontsize='small')
        ax5.grid(True, linestyle='--', alpha=0.5)

        # Etichette personalizzate sull'asse X
        ax5.set_xticks(x[::max(1, len(x) // 10)])  # Mostra circa 10 etichette
        ax5.set_xticklabels([data_filtered.index[i].strftime('%Y-%m-%d') for i in ax5.get_xticks()], rotation=45,
                            ha='right')

        self.plot_candlestick_chart(len(data_filtered))

        # Impostazioni finali del layout
        plt.tight_layout()
        plt.savefig("grafico_completo.png", dpi=300, bbox_inches='tight')  # Salva il grafico in alta qualità


        # Mostra il grafico in Streamlit
        st.pyplot(fig)

        # Mantieni la struttura chiamando il grafico a candele separatamente
        plt.close()



