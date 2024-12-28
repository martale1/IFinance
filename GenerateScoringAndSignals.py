import json


from TickerDownloaderScoringAndSignals import TickerDownloaderScoringAndSignals

class GenerateScoringAndSignals:
    def print_variables(self):
        for var_name, value in vars(self).items():
            print(f"{var_name}: {value}")

    def __init__(self, ticker,ticker_name,ema_period,candles=0,period='2y'):
        self.data = None
        self.ema_period = ema_period
        self.ticker = ticker
        self.ticker_name=ticker_name
        self.trading_indication1 = None
        self.trading_indication2=None
        self.trading_indication3=None
        self.trading_indication4=None
        self.signal1=None
        self.signal2=None
        self.signal3=None
        self.signal4=None
        self.signal5=None
        self.signal6=None
        self.prompt = None
        self.candlesticksAndTAindicatorsString = None
        self.candlesDataFrame=None
        self.period=period
        self.download_data(candles=candles)

    def TS1(self):
        # Genera segnali basati su condizioni utilizzando indicatori TA esistenti
        ema_period = self.ema_period
        self.data['TrendIndicator1'] = 0
        # EMA<Close; Close<SAR; MACD>Signal
        self.data.loc[
            (self.data[f'EMA_{ema_period}'] < self.data['Close']) & (self.data['SAR'] < self.data['Close']) & (
                        self.data['MACD'] > self.data['MACD_Signal']), 'TrendIndicator1'] = 1
        self.data.loc[
            (self.data[f'EMA_{ema_period}'] >= self.data['Close']) & (self.data['SAR'] >= self.data['Close']) & (
                        self.data['MACD'] <= self.data['MACD_Signal']), 'TrendIndicator1'] = -1
        self.trading_indication1 = 1 if self.data['TrendIndicator1'].iloc[-1] == 1 else (
            -1 if self.data['TrendIndicator1'].iloc[-1] == -1 else 0)

        self.data['TrendIndicator2'] = 0
        # EMA<Close;SAR<Close;ADX>25; DX+>DX-
        self.data.loc[
            (self.data[f'EMA_{ema_period}'] < self.data['Close']) & (self.data['SAR'] < self.data['Close']) & (
                        self.data['ADX'] > 25) & (self.data['+DX'] > self.data['-DX']), 'TrendIndicator2'] = 1
        self.data.loc[
            (self.data[f'EMA_{ema_period}'] >= self.data['Close']) & (self.data['SAR'] >= self.data['Close']) & (
                        self.data['ADX'] <= 25) & (self.data['+DX'] <= self.data['-DX']), 'TrendIndicator2'] = -1
        self.trading_indication2 = 1 if self.data['TrendIndicator2'].iloc[-1] == 1 else (
            -1 if self.data['TrendIndicator2'].iloc[-1] == -1 else 0)

        self.data['TrendIndicator3'] = 0
        # EMA<Close; StoK>StoD or StoK>70; MACD>Signal
        # self.data.loc[(self.data[f'EMA_{ema_period}'] < self.data['Close']) & (self.data['Stochastic_K'] > self.data['Stochastic_D'] or self.data['Stochastic_K'] >70 )  & (self.data['MACD'] > self.data['MACD_Signal']), 'Signal3'] = 1
        self.data.loc[(self.data[f'EMA_{ema_period}'] < self.data['Close']) & (
                (self.data['Stochastic_K'] > self.data['Stochastic_D']) | (self.data['Stochastic_K'] > 70)) & (
                              self.data['MACD'] > self.data['MACD_Signal']), 'TrendIndicator3'] = 1

        # self.data.loc[(self.data[f'EMA_{ema_period}'] >= self.data['Close']) & (self.data['Stochastic_K'] <= self.data['Stochastic_D'] or self.data['Stochastic_K'] <=30  ) & (self.data['MACD'] <= self.data['MACD_Signal']), 'Signal3'] = -1

        self.data.loc[(self.data[f'EMA_{ema_period}'] >= self.data['Close']) & (
                (self.data['Stochastic_K'] <= self.data['Stochastic_D']) | (self.data['Stochastic_K'] <= 30)) & (
                              self.data['MACD'] <= self.data['MACD_Signal']), 'TrendIndicator3'] = -1
        self.trading_indication3 = 1 if self.data['TrendIndicator3'].iloc[-1] == 1 else (
            -1 if self.data['TrendIndicator3'].iloc[-1] == -1 else 0)

        self.data['TrendIndicator4'] = 0
        # EMA<Close; Lips>Teeth; Teeth>Jaw' Close>Lips Clos>Lips
        self.data.loc[(self.data['Close'] > self.data['Alligator_Lips']) & (
                    self.data[f'EMA_{ema_period}'] < self.data['Close']) & (
                                  self.data['Alligator_Lips'] > self.data['Alligator_Teeth']) & (
                                  self.data['Alligator_Teeth'] > self.data['Alligator_Jaw']), 'TrendIndicator4'] = 1
        self.data.loc[((self.data['Close'] > self.data['Alligator_Lips']) & self.data[f'EMA_{ema_period}'] >=
                       self.data['Close']) & (self.data['Alligator_Lips'] <= self.data['Alligator_Teeth']) & (
                                  self.data['Alligator_Teeth'] <= self.data[
                              'Alligator_Jaw']), 'TrendIndicator4'] = -1
        self.trading_indication4 = 1 if self.data['TrendIndicator4'].iloc[-1] == 1 else (
            -1 if self.data['TrendIndicator4'].iloc[-1] == -1 else 0)

        ###$$$$$$$$$$$$$$$$ Generazione Segnali $$$$$$$$$$$$$$$$$
        # Genera 1 se MACD Crossing Above Signal
        # Genera -1 se MACD Crossing Below Signal
        # Genera 0 in tutti gli altri casi

        self.data['Signal1'] = 0
        self.data.loc[(self.data[f'EMA_{ema_period}'] < self.data['Close']) &
                      # (self.data['Stochastic_K'] <= 60) &
                      (self.data['MACD'] > self.data['MACD_Signal']) &
                      (self.data['MACD'].shift(1) <= self.data['MACD_Signal'].shift(1)), 'Signal1'] = 1

        self.data.loc[(self.data[f'EMA_{ema_period}'] < self.data['Close']) &
                      # (self.data['Stochastic_K'] > 70) &
                      (self.data['MACD'] < self.data['MACD_Signal']) &
                      (self.data['MACD'].shift(1) >= self.data['MACD_Signal'].shift(1)), 'Signal1'] = -1
        # Assegna il valore dell'indicatore di trading al valore finale della colonna
        self.signal1 = 1 if self.data['Signal1'].iloc[-1] == 1 else (
            -1 if self.data['Signal1'].iloc[-1] == -1 else 0)

        ### Signal2 Inizio ######
        # Genera 1 se K>20 e K_prec<=20_prec
        # Genera -1 se se K<70 e K_prec>=70
        # Genera 0 in tutti gli altri casi
        # Inizializza la colonna Signal2 con 0
        self.data['Signal2'] = 0

        # Condizione 1: Genera 1 se K > 20 e K_prec <= 20_prec
        self.data.loc[
            (self.data['Stochastic_K'] > 20) &
            (self.data['Stochastic_K'].shift(1) <= 20), 'Signal2'] = 1

        # Condizione 2: Genera 2 se K > 0, ieri > 0 e due giorni fa <= 0
        self.data.loc[
            (self.data['Stochastic_K'] > 20) &
            (self.data['Stochastic_K'].shift(1) > 20) &
            (self.data['Stochastic_K'].shift(2) <= 20), 'Signal2'] = 2

        # Condizione 3: Genera 3 se K > 0, ieri > 0, due giorni fa > 0 e tre giorni fa <= 0
        self.data.loc[
            (self.data['Stochastic_K'] > 20) &
            (self.data['Stochastic_K'].shift(1) > 20) &
            (self.data['Stochastic_K'].shift(2) > 20) &
            (self.data['Stochastic_K'].shift(3) <= 20), 'Signal2'] = 3

        # Condizione 4: Genera -1 se K < 70 e K_prec >= 70
        self.data.loc[
            (self.data['Stochastic_K'] < 70) &
            (self.data['Stochastic_K'].shift(1) >= 70), 'Signal2'] = -1

        # Restituisci il valore finale di Signal2 per l'ultima riga del DataFrame
        self.signal2 = self.data['Signal2'].iloc[-1] if not self.data.empty else 0

        ######### Signal2 fine

        # -------------------------    Signal3    # Inizializziamo Signal3 come 0
        # ------------------------- Signal3 -------------------------

        # Inizializziamo Signal3 come 0
        self.data['Signal3'] = 0

        # Condizione 1: MACD diventa positivo rispetto al giorno precedente (da <= 0 a > 0)
        condizione_1 = (self.data['MACD'] > 0) & (self.data['MACD'].shift(1) <= 0)
        self.data.loc[condizione_1, 'Signal3'] = 1

        # Condizione 2: MACD > 0, maggiore del giorno precedente (> 0), e due giorni fa MACD <= 0
        condizione_2 = (
                (self.data['MACD'] > 0) &
                (self.data['MACD'] > self.data['MACD'].shift(1)) &
                (self.data['MACD'].shift(1) > 0) &
                (self.data['MACD'].shift(2) <= 0)
        )
        self.data.loc[condizione_2, 'Signal3'] = 2

        # Condizione 3: MACD > MACD (giorno precedente) > MACD (due giorni prima) > 0, e tre giorni fa MACD <= 0
        condizione_3 = (
                (self.data['MACD'] > self.data['MACD'].shift(1)) &
                (self.data['MACD'].shift(1) > self.data['MACD'].shift(2)) &
                (self.data['MACD'].shift(2) > 0) &
                (self.data['MACD'].shift(3) <= 0)
        )
        self.data.loc[condizione_3, 'Signal3'] = 3

        # Condizione per -1: MACD diventa negativo rispetto al giorno precedente (da > 0 a <= 0)
        condizione_negativa = (self.data['MACD'] < 0) & (self.data['MACD'].shift(1) >= 0)
        self.data.loc[condizione_negativa, 'Signal3'] = -1

        # Determina il valore finale di Signal3
        self.signal3 = self.data['Signal3'].iloc[-1]

        # ------------------ end signal3

        # ----------------- SignalS4 con RSI

        # Inizializziamo Signal4 a 0. Questo crea problemi di performance
        self.data['Signal4'] = 0
        # Buy Signal (1) quando l'RSI supera 50
        self.data.loc[(self.data['RSI'] > 50) & (self.data['RSI'].shift(1) <= 50), 'Signal4'] = 1
        # Sell Signal (-1) quando l'RSI scende sotto 50
        self.data.loc[(self.data['RSI'] < 50) & (self.data['RSI'].shift(1) >= 50), 'Signal4'] = -1
        # Assegna il valore dell'indicatore di trading al valore finale della colonna
        self.signal4 = 1 if self.data['Signal4'].iloc[-1] == 1 else (
            -1 if self.data['Signal4'].iloc[-1] == -1 else 0)

        # ----------------------------------  Signal5  Bande di bollinger
        # Bollinger Bands rule for Signal5
        self.data['Signal5'] = 0
        # Generate signal 1 if the closing price is above the upper Bollinger Band and the previous 3 closes were below the upper Bollinger Band
        self.data.loc[
            (self.data['Close'] > self.data['Bollinger_Upper']) &
            (self.data['Close'].shift(1) <= self.data['Bollinger_Upper'].shift(1)) &
            (self.data['Close'].shift(2) <= self.data['Bollinger_Upper'].shift(2)) &
            (self.data['Close'].shift(3) <= self.data['Bollinger_Upper'].shift(3)), 'Signal5'] = 1
        # Generate signal -1 if the closing price is below the lower Bollinger Band and the previous 3 closes were above the lower Bollinger Band
        self.data.loc[
            (self.data['Close'] < self.data['Bollinger_Lower']) &
            (self.data['Close'].shift(1) >= self.data['Bollinger_Lower'].shift(1)) &
            (self.data['Close'].shift(2) >= self.data['Bollinger_Lower'].shift(2)) &
            (self.data['Close'].shift(3) >= self.data['Bollinger_Lower'].shift(3)), 'Signal5'] = -1

        # Assign the final signal value for Signal5
        self.signal5 = 1 if self.data['Signal5'].iloc[-1] == 1 else (
            -1 if self.data['Signal5'].iloc[-1] == -1 else 0)

        # s6 calculation
        # Initialize the s6 column
        self.data['Signal6'] = 'sleep1'  # Default value

        # Define the conditions for each s6 value
        self.data.loc[(self.data['Alligator_Lips'] > self.data['Close']) &
                      (self.data['Alligator_Lips'] < self.data['Alligator_Teeth']) & (
                              self.data['Alligator_Teeth'] < self.data['Alligator_Jaw']), 'Signal6'] = 'Downtrend'

        # Modify the 'Downtrend' signal to 'Downtrend*' if the previous day was not 'Downtrend'
        self.data.loc[(self.data['Signal6'] == 'Downtrend') &
                      (self.data['Signal6'].shift(1) != 'Downtrend'), 'Signal6'] = 'Downtrend*'

        self.data.loc[(self.data['Alligator_Lips'] < self.data['Close']) &
                      (self.data['Alligator_Lips'] < self.data['Alligator_Teeth']) & (
                              self.data['Alligator_Teeth'] < self.data[
                          'Alligator_Jaw']), 'Signal6'] = 'Downtrend_revS3Sig+'

        self.data.loc[(self.data['Alligator_Teeth'] < self.data['Close']) &
                      (self.data['Alligator_Lips'] < self.data['Alligator_Teeth']) & (
                              self.data['Alligator_Teeth'] < self.data[
                          'Alligator_Jaw']), 'Signal6'] = 'Downtrend_revS3Sig++'

        self.data.loc[(self.data['Alligator_Jaw'] < self.data['Close']) &
                      (self.data['Alligator_Lips'] < self.data['Alligator_Teeth']) & (
                              self.data['Alligator_Teeth'] < self.data[
                          'Alligator_Jaw']), 'Signal6'] = 'Downtrend_revS3Sig+++'

        self.data.loc[
            (self.data['Alligator_Lips'] >= self.data['Close']) &  # Uptrend con Price(Close) sotto Lips(Green)
            (self.data['Alligator_Jaw'] < self.data['Alligator_Teeth']) & (
                    self.data['Alligator_Teeth'] < self.data['Alligator_Lips']), 'Signal6'] = 'Uptrend-'

        self.data.loc[
            (self.data['Alligator_Teeth'] >= self.data['Close']) &  # Uptrend con Price(Close) sotto Teeth(Red)
            (self.data['Alligator_Jaw'] < self.data['Alligator_Teeth']) & (
                    self.data['Alligator_Teeth'] < self.data['Alligator_Lips']), 'Signal6'] = 'Uptrend--'

        self.data.loc[
            (self.data['Alligator_Jaw'] >= self.data['Close']) &  # Uptrend con Price(Close) sotto Jaw (Blue)
            (self.data['Alligator_Jaw'] < self.data['Alligator_Teeth']) & (
                    self.data['Alligator_Teeth'] < self.data['Alligator_Lips']), 'Signal6'] = 'Uptrend---'

        # self.data.loc[(self.data['Alligator_Lips'] >= self.data['Close']) & #Uptrend con Price(Close) sotto Lips(Green)
        #       (self.data['Alligator_Jaw'] < self.data['Alligator_Teeth']) & (
        #        self.data['Alligator_Teeth'] < self.data['Alligator_Lips']), 'Signal6'] = 'Uptrend-'

        self.data.loc[
            (self.data['Alligator_Lips'] < self.data['Close']) &  # Uptrend con Price(Close) sopra Lips(Green)
            (self.data['Alligator_Jaw'] < self.data['Alligator_Teeth']) & (
                    self.data['Alligator_Teeth'] < self.data['Alligator_Lips']), 'Signal6'] = 'Uptrend'
        # Modify the 'Uptrend' signal to 'Uptrend*' if the previous day was not 'Uptrend'
        self.data.loc[(self.data['Signal6'] == 'Uptrend') &
                      (self.data['Signal6'].shift(1) != 'Uptrend'), 'Signal6'] = 'Uptrend*'

        self.data.loc[(self.data['Alligator_Jaw'] < self.data['Alligator_Lips']) & (
                self.data['Alligator_Lips'] < self.data['Alligator_Teeth']), 'Signal6'] = 'sleep1'

        self.data.loc[(self.data['Alligator_Lips'] < self.data['Alligator_Jaw']) & (
                self.data['Alligator_Jaw'] < self.data['Alligator_Teeth']), 'Signal6'] = 'sleep2'

        self.data.loc[(self.data['Alligator_Lips'] < self.data['Close']) &
                      (self.data['Alligator_Teeth'] < self.data['Alligator_Lips']) & (
                              self.data['Alligator_Lips'] < self.data['Alligator_Jaw']), 'Signal6'] = 'wakeup1'

        self.data.loc[(self.data['Alligator_Lips'] >= self.data['Close']) &
                      (self.data['Alligator_Teeth'] < self.data['Alligator_Lips']) & (
                              self.data['Alligator_Lips'] < self.data['Alligator_Jaw']), 'Signal6'] = 'wakeup1-'

        self.data.loc[(self.data['Alligator_Lips'] < self.data['Close']) &
                      (self.data['Alligator_Teeth'] < self.data['Alligator_Jaw']) & (
                              self.data['Alligator_Jaw'] < self.data['Alligator_Lips']), 'Signal6'] = 'wakeup2'

        # Modify the 'wakeup2' signal to 'wakeup2*' if the previous day was not 'wakeup2'
        self.data.loc[(self.data['Signal6'] == 'wakeup2') &
                      (self.data['Signal6'].shift(1) != 'wakeup2'), 'Signal6'] = 'wakeup2*'

        self.data.loc[(self.data['Alligator_Lips'] >= self.data['Close']) &
                      (self.data['Alligator_Teeth'] < self.data['Alligator_Jaw']) & (
                              self.data['Alligator_Jaw'] < self.data['Alligator_Lips']), 'Signal6'] = 'wakeup2-'

        self.signal6 = self.data['Signal6'].iloc[-1]

        # extract last row and add ticker and ticker name
        last_row = self.data.iloc[[-1]].copy()
        last_row['Ticker'] = self.ticker
        last_row['Ticker Name'] = self.ticker_name

        return last_row  # Return the last row of data



    def run(self):
        return self.TS1()

    def get_candlesticks_andTAindicators_string(self):
        return self.candlesticksAndTAindicators

    def download_data(self,candles):
        stock = TickerDownloaderScoringAndSignals(self.ticker, self.period)
        stock.download_data(ema_period=self.ema_period, macd_fast_period=12, macd_slow_period=26, macd_signal_period=9, sar_af=0.02, sar_max_af=0.2, adx_period=14)

        if candles:
            if (len(stock.data)>10):
                stock.generate_dfWithCandleStickListSummaryColumn()
        self.candlesDataFrame=stock.candles
        self.data = stock.data
        self.candlesticksAndTAindicatorsString=stock.get_candlesticks_andTAindicators_string()

    def download_json(self):
        # Controlla se i dati esistono
        if self.data is None:
            raise ValueError("I dati non sono stati scaricati. Esegui prima il metodo 'download_data()'.")
        # Estrarre l'ultima riga (che rappresenta i segnali generati)
        last_row = self.TS1()
        # Convertire il DataFrame in formato JSON
        data_json = last_row.to_json(orient='records')  # Converte la riga in formato JSON
        # Convertire il JSON in un oggetto Python (dizionario) per ulteriori manipolazioni
        data_dict = json.loads(data_json)
        # Rimuovere i campi 'Ticker' e 'Ticker Name' da signals
        if 'Ticker' in data_dict[0]:
            del data_dict[0]['Ticker']
        if 'Ticker Name' in data_dict[0]:
            del data_dict[0]['Ticker Name']
        # Creare la struttura finale del JSON senza i campi 'Ticker' e 'Ticker Name' dentro 'signals'
        response = {
            "ticker": self.ticker,
            "ticker_name": self.ticker_name,
            "signals": data_dict  # Questo contiene l'ultima riga dei segnali senza 'Ticker' e 'Ticker Name'
        }
        # Restituisce la stringa JSON
        return json.dumps(response, indent=4)


'''
ticker='LCOC.MI'
ticker_name='LCOC.MI'
ts = GenerateScoringAndSignals(ticker, ticker_name, ema_period=50, period='2y', candles=0)
ts.run()
#print(ts.data.to_string())
json_data = ts.download_json()
print(json_data)
from dbTickersData import dbTickersData
dbT=dbTickersData()
dbT.save_json_data(json_data, "IT", "ETF")
print("Added")
jj=dbT.load_json_data("LCOC.MI")
print(jj)


import pandas as pd
df = ts.run()
# Ensure the index is a DatetimeIndex
df.index = pd.to_datetime(df.index, errors='coerce')  # Convert index to datetime; handle errors if any.

# Current date
current_date = pd.Timestamp.now()

# Calculate the difference in days
days_diff = (current_date - df.index).days.astype(int)  # Converte a intero

# Stampa la differenza
print("Differenza in giorni (interi):")
print(days_diff)
if days_diff==0:
    print("OK")
elif(days_diff>228):
    print("Maggiore di zero")
#json_data = ts.download_json()
#print(json_data)
#dbT.save_json_data(json_data, nation, instrument_type)

#print(ts.data)
print(json_data)
from dbTickersData import dbTickersData
dbT=dbTickersData()
dbT.save_json_data(json_data, 'IT', 'ETC')
print(dbT.load_json_data('COCO.MI'))'''