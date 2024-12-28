
import talib
import yfinance as yf
import pandas as pd

class TickerDownloaderScoringAndSignals:
    #Function: (quelle utili sono le prime due)
    # get_candlesticks_string()
    # get_candlesticks_andTAindicators_string())

    # get_candlesticks_DF() Restituisce un dataframe con i pattern di candele per ogni giorno
    # generate_dfWithCandleStickListwithCDLplusCDLminus come precedente ed aggiunge cdl+ e cdl -
    # getCandlePattern (utilizzata da altre funzioni, non chiamabile direttamente)

    def __init__(self, name, period='2y',resolveTickerName=0):
#        self.name = name
        self.name = name.strip().replace(" ", "")

        self.period = period
        self.data = None
        self.ema_period='50'
        self.candles=pd.DataFrame()   #dataframe con le candele e l'aggiunta di CDL+ e CLD-
        if resolveTickerName:
            self.tickerName=self.get_ticker_name()

    def get_ticker_name(self):
        # Ottieni l'oggetto ticker
        #print(f"Ticker {self.name}")
        ticker = yf.Ticker(self.name)
        # Ottieni il nome del titolo
        ticker_info = ticker.info
        ticker_name = ticker_info['longName']

        return ticker_name




    def download_data(self, ema_period=50, macd_fast_period=12, macd_slow_period=26, macd_signal_period=9, sar_af=0.02, sar_max_af=0.2, adx_period=14):
        try:
          self.data = yf.download(self.name, period=self.period,progress=False)
          self.data = self.data.round(4)
          self.ema_period = ema_period
          # variazione percentuale
          self.data['Percent_Change_2'] = round(self.data['Close'].pct_change(periods=1) * 100, 2)
          self.data['Percent_Change_5'] = round(self.data['Close'].pct_change(periods=5) * 100, 2)
          self.data['Percent_Change_10'] = round(self.data['Close'].pct_change(periods=10) * 100, 2)
          self.data['Percent_Change_30'] = round(self.data['Close'].pct_change(periods=30) * 100, 2)

          # Calcola EMA ad n giorni
          self.data['EMA_' + str(ema_period)] = round(talib.EMA(self.data['Close'], timeperiod=ema_period), 2)

          # Calcola MACD
          macd, macd_signal, macd_histogram = talib.MACD(self.data['Close'], fastperiod=macd_fast_period,
                                                         slowperiod=macd_slow_period, signalperiod=macd_signal_period)
          self.data['MACD'] = round(macd, 4)
          self.data['MACD_Signal'] = round(macd_signal, 4)
          self.data['MACD_Histogram'] = round(macd_histogram, 4)
          self.data['MACD_Prev'] = self.data['MACD'].shift(1)
          self.data['MACD_Signal_Prev'] = self.data['MACD_Signal'].shift(1)
          # Calculate RSI
          rsi = talib.RSI(self.data['Close'], timeperiod=14)
          self.data['RSI'] = round(rsi, 2)
          # Calcola Parabolic SAR
          self.data['SAR'] = round(
              talib.SAR(self.data['High'], self.data['Low'], acceleration=sar_af, maximum=sar_max_af), 2)

          # Calcola ADX
          adx = talib.ADX(self.data['High'], self.data['Low'], self.data['Close'], timeperiod=adx_period)
          self.data['ADX'] = round(adx, 2)

          # Calcola +DX e -DX
          plus_dx = talib.PLUS_DI(self.data['High'], self.data['Low'], self.data['Close'], timeperiod=adx_period)
          minus_dx = talib.MINUS_DI(self.data['High'], self.data['Low'], self.data['Close'], timeperiod=adx_period)
          self.data['+DX'] = round(plus_dx, 2)
          self.data['-DX'] = round(minus_dx, 2)
          # Calculate Stochastic Oscillator
          stochastic_k_period = 14
          stochastic_d_period = 3
          stochastic_k, stochastic_d = talib.STOCH(self.data['High'], self.data['Low'], self.data['Close'],
                                                   fastk_period=stochastic_k_period, slowk_period=3,
                                                   slowd_period=stochastic_d_period)

          self.data['Stochastic_K'] = round(stochastic_k, 4)
          self.data['Stochastic_D'] = round(stochastic_d, 4)
          self.data['Stochastic_K_Prev'] =self.data['Stochastic_K'].shift(1)
          self.data['Stochastic_D_Prev'] =self.data['Stochastic_D'].shift(1)
          # Calculate Alligator indicator

          jaw_period = 13
          jaw_smooth=8
          teeth_period = 8
          teeth_smooth=5
          lips_period = 5
          lips_smoth=3

          jaw_sma1 = talib.SMA(self.data['Close'], timeperiod=jaw_period)
          teeth_sma1 = talib.SMA(self.data['Close'], timeperiod=teeth_period)
          lips_sma1 = talib.SMA(self.data['Close'], timeperiod=lips_period)
          jaw_sma = talib.SMA(jaw_sma1, timeperiod=jaw_smooth)
          teeth_sma = talib.SMA(teeth_sma1 , timeperiod=teeth_smooth)
          lips_sma = talib.SMA(lips_sma1, timeperiod=lips_smoth)


          self.data['Alligator_Jaw'] = round(jaw_sma, 4)
          self.data['Alligator_Teeth'] = round(teeth_sma, 4)
          self.data['Alligator_Lips'] = round(lips_sma, 4)

          # Calculating ATR
          atr_period = 14
          atr = talib.ATR(self.data['High'], self.data['Low'], self.data['Close'], timeperiod=atr_period)
          self.data['ATR'] = round(atr, 4)

          # Calcola ATR Trailing Stop Loss
          atr_multiplier = 3
          atr_trailing_stop_loss = self.data['Close'] - atr_multiplier * atr
          self.data['ATR_Trailing_Stop_Loss'] = round(atr_trailing_stop_loss, 4)

          # Calculate Bollinger Bands
          upper_band, middle_band, lower_band = talib.BBANDS(self.data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
          self.data['Bollinger_Upper'] = round(upper_band, 4)
          self.data['Bollinger_Middle'] = round(middle_band, 4)
          self.data['Bollinger_Lower'] = round(lower_band, 4)

          # Calcola Money Flow Index (MFI)
          self.data['MFI'] = round(
              talib.MFI(self.data['High'], self.data['Low'], self.data['Close'], self.data['Volume'], timeperiod=14), 2)

          # Adding the date of the latest quotation
          latest_quotation_date = self.data.index[-1]  # Get the last date in the index
          self.data['Date'] = latest_quotation_date
        except Exception as e:
          print(f"Failed to download data for {self.name}: {e}")
        #self.data = yf.download(self.name, period=self.period,progress=False)




    def getCandlePattern(self,last_day_patterns,log=0):

        if log:
            print("Ulimo giorno pattern")
            print(f"{last_day_patterns}")
            print(f"Lunghezza patterns {len(last_day_patterns)}")
        # close_price = round(self.data['Close'].iloc[-1], 2)
        # lista_items = f"Close={close_price}, "
        lista_items = ''
        for indice in range(33, len(last_day_patterns)):
            nome_colonna = last_day_patterns.index[indice]
            valore = last_day_patterns.iloc[indice]
            lista_items += f"{nome_colonna}={valore}, "
        if log:
            print("> Last data available in yf:", last_day_patterns.name)
            print(f"> Patterns on the last day: {len(last_day_patterns) - 26}")
            print("> Lista patterns for OPENAI:", lista_items)
        datePattern=last_day_patterns.name
        if len(lista_items)==0:
            lista_items='None'
        return lista_items,datePattern


    def get_candlesticks_DF(self, log=0):
        candle_names = talib.get_function_groups()["Pattern Recognition"]
        for candle in candle_names:
            self.data[candle] = getattr(talib, candle)(self.data["Open"], self.data["High"], self.data["Low"], self.data["Close"])
        #print(f"Numero entry{len(self.data)}")
        candle_patterns_df = pd.DataFrame(columns=["Date","Candle_Patterns" ])
        for i in range(len(self.data)):
            last_day_patterns = self.data.iloc[i][self.data.iloc[i] != 0]
            lista_candles,datePattern=self.getCandlePattern(last_day_patterns,0)
            #print(f"{lista_candles} {datePattern}")
            new_row = {"Date": datePattern,"Candle_Patterns": lista_candles }
            candle_patterns_df = pd.concat([candle_patterns_df, pd.DataFrame([new_row])], ignore_index=True)
        candle_patterns_df.set_index("Date", inplace=True)
        return candle_patterns_df



    def generate_dfWithCandleStickListwithCDLplusCDLminus(self):
        #it creates a column containing the list of candlestick with value
        candle_names = talib.get_function_groups()["Pattern Recognition"]
        for candle in candle_names:
            self.candles[candle] = getattr(talib, candle)(self.data["Open"], self.data["High"], self.data["Low"],
                                                       self.data["Close"])

        # Assuming df is your DataFrame with candlestick patterns
        # Initialize an empty list to hold the results
        summary_list = []

        # Iterate over each row in the DataFrame
        for index, row in self.candles.iterrows():
            # Initialize an empty list to store non-zero column names and values
            summary = []
            # Iterate over each column
            for column in self.candles.columns:
                value = row[column]
                # Check if the value is not zero
                if value != 0:
                    # Append the column name and value to the summary list
                    summary.append(f"{column}={value}")
            # Join the summary list elements into a single string separated by ', '
            summary_list.append(', '.join(summary))

        # Add the summary list as a new column to the original DataFrame



        self.candles['summary'] = summary_list
        #self.candles['cdlplus'] = self.candles['summary'].apply(lambda x: x.count('=100'))
        #self.candles['cdlminus'] = self.candles['summary'].apply(lambda x: x.count('=-100'))
        # Estrarre i numeri dalla colonna 'summary' e sommare quelli positivi in 'cdlplus' e quelli negativi in 'cdlminus'
        self.candles['cdlplus'] = self.candles['summary'].str.findall(r'=(-?\d+)').apply(
            lambda x: sum(int(val) for val in x if int(val) > 0))
        self.candles['cdlminus'] = self.candles['summary'].str.findall(r'=(-?\d+)').apply(
            lambda x: sum(int(val) for val in x if int(val) < 0))

    def get_candlesticks_string(self, log=0):
        """
        Raccoglie le informazioni sui pattern delle candele (CDL) e la data, e restituisce una stringa formattata.
        Args:
        log (int): Se impostato a 1, stampa i risultati intermedi per il debug.
        Returns:
        str: Stringa con informazioni sui pattern delle candele e la data.
        """
        # Ottieni tutti i pattern di candele di TA-Lib
        candle_names = talib.get_function_groups()["Pattern Recognition"]

        # Calcola i valori per ciascun pattern di candele e aggiungili al dataframe
        for candle in candle_names:
            self.data[candle] = getattr(talib, candle)(self.data["Open"], self.data["High"], self.data["Low"],
                                                       self.data["Close"])

        # Verifica se ci sono dati disponibili
        if len(self.data) > 0:
            # Prendi tutti i pattern dell'ultimo giorno in cui non sono nulli
            last_day_patterns = self.data.iloc[-1][self.data.iloc[-1] != 0]
        else:
            last_day_patterns = ''

        if log:
            print(f"Pattern estratti per l'ultimo giorno: {last_day_patterns}")

        # Ottieni la data dell'ultima riga
        date_value = self.data.index[-1] if len(self.data) > 0 else 'N/A'
        lista_items = f"Date={date_value}, "

        # Aggiungi solo i pattern di candele dell'ultimo giorno
        for indice in range(0, len(last_day_patterns)):
            nome_colonna = last_day_patterns.index[indice]
            valore = last_day_patterns.iloc[indice]
            if "CDL" in nome_colonna:  # Includi solo le colonne che sono pattern di candele
                lista_items += f"{nome_colonna}={valore}, "

        if log:
            print("> Lista patterns per OPENAI:", lista_items)

        # Rimuovi l'ultima virgola e spazio aggiunti e restituisci la stringa
        return lista_items.rstrip(", ")

    def get_candlesticks_andTAindicators_string(self, log=0):
        candle_names = talib.get_function_groups()["Pattern Recognition"]
        for candle in candle_names:
            self.data[candle] = getattr(talib, candle)(self.data["Open"], self.data["High"], self.data["Low"], self.data["Close"])
        if len(self.data)>0:
            last_day_patterns = self.data.iloc[-1][self.data.iloc[-1] != 0]
        else:
            last_day_patterns=''

        if log:
            print(f"{last_day_patterns}")
        if len(self.data)>0:
            close_price = round(self.data['Close'].iloc[-1], 2)
        else:
            close_price=None
        lista_items = f"Close={close_price}, "
        for indice in range(6, len(last_day_patterns)):
            nome_colonna = last_day_patterns.index[indice]
            valore = last_day_patterns.iloc[indice]
            lista_items += f"{nome_colonna}={valore}, "
        if log:
          print("> Last data available in yf:", last_day_patterns.name)
          print(f"> Patterns on the last day: {len(last_day_patterns) - 6}")
          print("> Lista patterns for OPENAI:", lista_items)
        return lista_items