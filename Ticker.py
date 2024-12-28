import re
from TickerDownloaderScoringAndSignals import TickerDownloaderScoringAndSignals
from GenerateScoringAndSignals import GenerateScoringAndSignals
import json

class Ticker:
    def __init__(self, ticker: str, ticker_name: str = ""):
        """
        Inizializza un'istanza della classe Ticker con i campi base.
        """
        self.ticker = ticker
        self.ticker_name = ticker_name

        # Campi derivati da TradingSystems e TickerAnalyzer
        self.scoring = ""
        self.signal1 = ""
        self.signal2 = ""
        self.signal3 = ""
        self.signal4 = ""
        self.signal5 = ""
        self.signal6 = ""
        self.trend_indicator1 = ""
        self.trend_indicator2 = ""
        self.trend_indicator3 = ""
        self.trend_indicator4 = ""

        # Altri campi di indicatori tecnici
        self.cdlplus = ""
        self.cdlminus = ""
        self.candlespattern = ""
        self.percent_change_2 = ""
        self.adx = ""
        self.volume = ""
        self.macd = ""
        self.macd_signal = ""
        self.macd_histogram = ""
        self.macd_prev = ""
        self.macd_signal_prev = ""
        self.rsi = ""
        self.stochastic_k = ""
        self.stochastic_d = ""
        self.stochastic_k_prev = ""
        self.stochastic_d_prev = ""
        self.ai = ""
        self.sar = ""
        self.close = ""
        self.percent_change_5 = ""
        self.atr = ""
        self.atr_trailing_stop_loss = ""
        self.dx_plus = ""
        self.dx_minus = ""
        self.percent_change_10 = ""
        self.percent_change_30 = ""
        self.open_price = ""
        self.high = ""
        self.low = ""
        self.date = ""
        self.adj_close = ""
        self.ema = ""
        self.alligator_jaw = ""
        self.alligator_teeth = ""
        self.alligator_lips = ""
        self.bollinger_upper = ""
        self.bollinger_middle = ""
        self.bollinger_lower = ""


    def generateTickerTAindicatorsScoringandSignals(self, period='2y', candles=0):

        #scarica i data e TA indicators
        tickerDownloaderInstance = TickerDownloaderScoringAndSignals(self.ticker, period=period)
        tickerDownloaderInstance.download_data()
        self.data=tickerDownloaderInstance.data
        self.populate_fields_with_ta_indicators(tickerDownloaderInstance) #popola dati oggetto con TA indicators

        #genera signals and scoring
        tradingSystemsAndSignalGeneratorInstance = GenerateScoringAndSignals(self.ticker, self.ticker_name, ema_period=tickerDownloaderInstance.ema_period, candles=candles)
        tradingSystemsAndSignalGeneratorInstance.run()

        #popola dati oggetto con signals e trend_indicators + scoring
        self.signal1 = tradingSystemsAndSignalGeneratorInstance.signal1
        self.signal2 = tradingSystemsAndSignalGeneratorInstance.signal2
        self.signal3 = tradingSystemsAndSignalGeneratorInstance.signal3
        self.signal4 = tradingSystemsAndSignalGeneratorInstance.signal4
        self.signal5 = tradingSystemsAndSignalGeneratorInstance.signal5
        self.signal6 = tradingSystemsAndSignalGeneratorInstance.data['Signal6'].iloc[-1]  # Prende l'ultimo valore di Signal6
        self.trend_indicator1 = tradingSystemsAndSignalGeneratorInstance.trading_indication1
        self.trend_indicator2 = tradingSystemsAndSignalGeneratorInstance.trading_indication2
        self.trend_indicator3 = tradingSystemsAndSignalGeneratorInstance.trading_indication3
        self.trend_indicator4 = tradingSystemsAndSignalGeneratorInstance.trading_indication4

        # Calcola lo scoring come somma dei trend indicator
        self.scoring = (self.trend_indicator1 or 0) + (self.trend_indicator2 or 0) + (self.trend_indicator3 or 0) + (self.trend_indicator4 or 0)

    def populate_fields_with_ta_indicators(self, tickerDownloaderInstance):

        self.ticker_name = tickerDownloaderInstance.get_ticker_name()  # Nome del ticker

        self.percent_change_2 = str(tickerDownloaderInstance.data['Percent_Change_2'].iloc[-1])
        self.percent_change_5 = str(tickerDownloaderInstance.data['Percent_Change_5'].iloc[-1])
        self.percent_change_10 = str(tickerDownloaderInstance.data['Percent_Change_10'].iloc[-1])
        self.percent_change_30 = str(tickerDownloaderInstance.data['Percent_Change_30'].iloc[-1])
        self.adx = str(tickerDownloaderInstance.data['ADX'].iloc[-1])
        self.volume = str(tickerDownloaderInstance.data['Volume'].iloc[-1])
        self.macd = str(tickerDownloaderInstance.data['MACD'].iloc[-1])
        self.macd_signal = str(tickerDownloaderInstance.data['MACD_Signal'].iloc[-1])
        self.macd_histogram = str(tickerDownloaderInstance.data['MACD_Histogram'].iloc[-1])
        self.macd_prev = str(tickerDownloaderInstance.data['MACD_Prev'].iloc[-1])
        self.macd_signal_prev = str(tickerDownloaderInstance.data['MACD_Signal_Prev'].iloc[-1])
        self.rsi = str(tickerDownloaderInstance.data['RSI'].iloc[-1])
        self.stochastic_k = str(tickerDownloaderInstance.data['Stochastic_K'].iloc[-1])
        self.stochastic_d = str(tickerDownloaderInstance.data['Stochastic_D'].iloc[-1])
        self.stochastic_k_prev = str(tickerDownloaderInstance.data['Stochastic_K_Prev'].iloc[-1])
        self.stochastic_d_prev = str(tickerDownloaderInstance.data['Stochastic_D_Prev'].iloc[-1])
        self.sar = str(tickerDownloaderInstance.data['SAR'].iloc[-1])
        self.close = str(tickerDownloaderInstance.data['Close'].iloc[-1])
        self.atr = str(tickerDownloaderInstance.data['ATR'].iloc[-1])
        self.atr_trailing_stop_loss = str(tickerDownloaderInstance.data['ATR_Trailing_Stop_Loss'].iloc[-1])
        self.dx_plus = str(tickerDownloaderInstance.data['+DX'].iloc[-1])
        self.dx_minus = str(tickerDownloaderInstance.data['-DX'].iloc[-1])
        self.open_price = str(tickerDownloaderInstance.data['Open'].iloc[-1])
        self.high = str(tickerDownloaderInstance.data['High'].iloc[-1])
        self.low = str(tickerDownloaderInstance.data['Low'].iloc[-1])
        self.date = str(tickerDownloaderInstance.data.index[-1])  # Ultima data disponibile nei dati
        self.adj_close = str(tickerDownloaderInstance.data['Adj Close'].iloc[-1])
        self.ema = str(tickerDownloaderInstance.data['EMA_' + str(tickerDownloaderInstance.ema_period)].iloc[-1])
        self.alligator_jaw = str(tickerDownloaderInstance.data['Alligator_Jaw'].iloc[-1])
        self.alligator_teeth = str(tickerDownloaderInstance.data['Alligator_Teeth'].iloc[-1])
        self.alligator_lips = str(tickerDownloaderInstance.data['Alligator_Lips'].iloc[-1])
        self.bollinger_upper = str(tickerDownloaderInstance.data['Bollinger_Upper'].iloc[-1])
        self.bollinger_middle = str(tickerDownloaderInstance.data['Bollinger_Middle'].iloc[-1])
        self.bollinger_lower = str(tickerDownloaderInstance.data['Bollinger_Lower'].iloc[-1])
        #queste sono le candele per AI bisogna semplificare e rimuovere TA indicators in funzione della libreriaAI
        self.candlespatternAndTA = tickerDownloaderInstance.get_candlesticks_andTAindicators_string()
        self.candlespattern=tickerDownloaderInstance.get_candlesticks_string()

    def __repr__(self):
        """
        Rappresentazione stringa dell'istanza del Ticker per il debug.
        """
        return f"Ticker({self.ticker}, {self.ticker_name}, Close: {self.close}, Percent Change 2: {self.percent_change_2},Percent Change 5: {self.percent_change_5}, Date: {self.date})"

    def to_json_with_ta_indicators(self):
        """
        Restituisce un JSON con i campi derivati da populate_fields_with_ta_indicators.
        """
        ta_indicators_data = {
            "ticker": self.ticker,
            "ticker_name": self.ticker_name,
            "percent_change_2": self.percent_change_2,
            "percent_change_5": self.percent_change_5,
            "percent_change_10": self.percent_change_10,
            "percent_change_30": self.percent_change_30,
            "adx": self.adx,
            "volume": self.volume,
            "macd": self.macd,
            "macd_signal": self.macd_signal,
            "macd_histogram": self.macd_histogram,
            "macd_prev": self.macd_prev,
            "macd_signal_prev": self.macd_signal_prev,
            "rsi": self.rsi,
            "stochastic_k": self.stochastic_k,
            "stochastic_d": self.stochastic_d,
            "stochastic_k_prev": self.stochastic_k_prev,
            "stochastic_d_prev": self.stochastic_d_prev,
            "sar": self.sar,
            "close": self.close,
            "atr": self.atr,
            "atr_trailing_stop_loss": self.atr_trailing_stop_loss,
            "dx_plus": self.dx_plus,
            "dx_minus": self.dx_minus,
            "open_price": self.open_price,
            "high": self.high,
            "low": self.low,
            "date": self.date,
            "adj_close": self.adj_close,
            "ema": self.ema,
            "alligator_jaw": self.alligator_jaw,
            "alligator_teeth": self.alligator_teeth,
            "alligator_lips": self.alligator_lips,
            "bollinger_upper": self.bollinger_upper,
            "bollinger_middle": self.bollinger_middle,
            "bollinger_lower": self.bollinger_lower,
            "candlespattern": self.candlespattern,
            "candlespatternAndTA": self.candlespatternAndTA #solo per controllare

        }
        return json.dumps(ta_indicators_data, indent=4)

    def to_json_with_scoring_and_signals(self):
        """
        Restituisce un JSON con i campi derivati da generateTickerTAindicatorsScoringandSignals.
        """
        scoring_signals_data = {
            "ticker": self.ticker,
            "ticker_name": self.ticker_name,
            "scoring": self.scoring,
            "signal1": self.signal1,
            "signal2": self.signal2,
            "signal3": self.signal3,
            "signal4": self.signal4,
            "signal5": self.signal5,
            "signal6": self.signal6,
            "trend_indicator1": self.trend_indicator1,
            "trend_indicator2": self.trend_indicator2,
            "trend_indicator3": self.trend_indicator3,
            "trend_indicator4": self.trend_indicator4
        }
        return json.dumps(scoring_signals_data, indent=4)

    def __repr__(self):
        """
        Rappresentazione stringa dell'istanza del Ticker per il debug.
        """
        return f"Ticker({self.ticker}, {self.ticker_name}, Close: {self.close}, Percent Change 2: {self.percent_change_2}, Percent Change 5: {self.percent_change_5}, Date: {self.date})"



def extract_candles_and_date(data_string):
    """
    Estrae le sottostringhe che contengono le informazioni sulle candele e la data dalla stringa fornita.

    Args:
    data_string (str): La stringa che contiene i vari valori separati da virgole.

    Returns:
    dict: Un dizionario con le chiavi e i valori relativi a candele e data.
    """
    # Pattern per estrarre le chiavi che contengono 'Date' oppure 'CDL'
    pattern = r'(\b(?:CDL\w+|Date)\b=[^,]+)'

    # Trova tutte le corrispondenze del pattern
    matches = re.findall(pattern, data_string)

    # Crea un dizionario per le chiavi e i valori estratti
    result = {}
    for match in matches:
        key, value = match.split('=')
        result[key] = value.strip()

    return result

def populate_fields_with_ta_indicators(self, tickerDownloaderInstance):
    """
    Popola i campi dell'oggetto Ticker con gli indicatori TA forniti da tickerDownloaderInstance.
    """
    if tickerDownloaderInstance.data is not None:
        if 'Percent_Change_2' in tickerDownloaderInstance.data.columns:
            self.percent_change_2 = str(tickerDownloaderInstance.data['Percent_Change_2'].iloc[-1])
        else:
            self.percent_change_2 = None  # Gestisci il caso in cui il campo non esista

        if 'Percent_Change_5' in tickerDownloaderInstance.data.columns:
            self.percent_change_5 = str(tickerDownloaderInstance.data['Percent_Change_5'].iloc[-1])
        else:
            self.percent_change_5 = None

        # Continua con altri campi necessari...
    else:
        print(f"Dati TA non disponibili per il ticker {self.ticker}.")
'''
t=Ticker('lnga.mi','3cfl.mi')
t.generateTickerTAindicatorsScoringandSignals()
print(t.percent_change_2)
print(t.close)
print(t.date)
print(t.data['Close'])'''