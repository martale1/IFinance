import json
import sqlite3
import pandas as pd
class dbTickersData:
    def __init__(self, db_path="/home/developer/PycharmProjects/learningProjects/IFinance/stock_data7.db"):
        # Crea o connette il database SQLite
        self.conn = sqlite3.connect(db_path,check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Crea una tabella per memorizzare i dati del JSON, con aggiunta di `nation`, `instrument_type`, e `Scoring`
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS json_data (
                ticker TEXT PRIMARY KEY,
                ticker_name TEXT,
                nation TEXT,
                instrument_type TEXT,
                open TEXT,
                high TEXT,
                low TEXT,
                close TEXT,
                adj_close TEXT,
                volume REAL,
                percent_change_2 REAL,
                percent_change_5 REAL,
                percent_change_10 REAL,
                percent_change_30 REAL,
                ema_50 TEXT,
                macd TEXT,
                macd_signal TEXT,
                macd_histogram TEXT,
                macd_prev TEXT,
                macd_signal_prev TEXT,
                rsi TEXT,
                sar TEXT,
                adx TEXT,
                plus_dx TEXT,
                minus_dx TEXT,
                stochastic_k TEXT,
                stochastic_d TEXT,
                stochastic_k_prev TEXT,
                stochastic_d_prev TEXT,
                alligator_jaw TEXT,
                alligator_teeth TEXT,
                alligator_lips TEXT,
                atr TEXT,
                atr_trailing_stop_loss TEXT,
                bollinger_upper TEXT,
                bollinger_middle TEXT,
                bollinger_lower TEXT,
                mfi REAL, -- Aggiunta della colonna MFI
                date TEXT,
                trend_indicator1 TEXT,
                trend_indicator2 TEXT,
                trend_indicator3 TEXT,
                trend_indicator4 TEXT,
                scoring INTEGER, -- Aggiunta della colonna `Scoring`
                signal1 TEXT,
                signal2 TEXT,
                signal3 TEXT,
                signal4 TEXT,
                signal5 TEXT,
                signal6 TEXT,
                cdl_patterns TEXT -- Riassunto dei pattern CDL memorizzati come stringa
            )
        ''')
        self.conn.commit()
    def load_json_data(self, ticker):
        # Carica i dati dal database per un ticker specifico
        self.cursor.execute('SELECT * FROM json_data WHERE ticker = ?', (ticker,))
        result = self.cursor.fetchone()

        if result:
            # Creiamo un dizionario dai dati estratti dal database
            data = {
                'ticker': result[0],
                'ticker_name': result[1],
                'nation': result[2],
                'instrument_type': result[3],
                'signals': [{
                    'Open': result[4], 'High': result[5], 'Low': result[6], 'Close': result[7], 'Adj Close': result[8],
                    'Volume': result[9], 'Percent_Change_2': result[10], 'Percent_Change_5': result[11],
                    'Percent_Change_10': result[12], 'Percent_Change_30': result[13], 'EMA_50': result[14],
                    'MACD': result[15], 'MACD_Signal': result[16], 'MACD_Histogram': result[17],
                    'MACD_Prev': result[18], 'MACD_Signal_Prev': result[19], 'RSI': result[20], 'SAR': result[21], 'ADX': result[22],
                    '+DX': result[23], '-DX': result[24], 'Stochastic_K': result[25], 'Stochastic_D': result[26],
                    'Stochastic_K_Prev': result[27], 'Stochastic_D_Prev': result[28], 'Alligator_Jaw': result[29],
                    'Alligator_Teeth': result[30], 'Alligator_Lips': result[31], 'ATR': result[32],
                    'ATR_Trailing_Stop_Loss': result[33], 'Bollinger_Upper': result[34], 'Bollinger_Middle': result[35],
                    'Bollinger_Lower': result[36], 'MFI': result[37], 'Date': result[38], 'TrendIndicator1': result[39],
                    'TrendIndicator2': result[40], 'TrendIndicator3': result[41], 'TrendIndicator4': result[42],
                    'Scoring': result[43],  # Aggiunta del campo Scoring
                    'Signal1': result[44], 'Signal2': result[45], 'Signal3': result[46], 'Signal4': result[47],
                    'Signal5': result[48], 'Signal6': result[49], 'CDL_Patterns': result[50]
                }]
            }
            return data
        else:
            print(f"Nessun dato trovato per {ticker}")
            return None


    def delete_json_data(self, ticker):
        # Elimina i dati per un ticker specifico
        self.cursor.execute('DELETE FROM json_data WHERE ticker = ?', (ticker,))
        self.conn.commit()
        print(f"Dati eliminati per {ticker}")

    def search_signal3_greater_than_zero(self):
        # Esegui una query per ottenere i ticker con Signal3 > 0
        self.cursor.execute('SELECT ticker, ticker_name, signal3 FROM json_data WHERE signal3 > "0"')
        results = self.cursor.fetchall()

        if results:
            #print("Tickers con Signal3 > 0:")
            #for result in results:
                #print(f"Ticker: {result[0]}, Nome: {result[1]}, Signal3: {result[2]}")
            return results
        else:
            print("Nessun ticker trovato con Signal3 > 0")
            return None

    def close(self):
        # Chiude la connessione al database
        self.conn.close()

    def count_entries(self):
        # Esegui una query per contare il numero di voci nel database
        self.cursor.execute('SELECT COUNT(*) FROM json_data')
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return 0

    def get_top_n_tickers_by_percent_change(self, nation, instrument_type, days, limit=10):
        # Mappa i valori dei giorni nei rispettivi campi di percentuale di variazione
        days_to_field = {
            2: 'percent_change_2',
            5: 'percent_change_5',
            10: 'percent_change_10',
            30: 'percent_change_30'
        }

        # Controlla se il valore dei giorni è valido
        if days not in days_to_field:
            raise ValueError("Invalid value for days. Choose from 2, 5, 10, or 30.")

        # Ottieni il campo corretto in base al numero di giorni
        percent_change_field = days_to_field[days]

        # Se top_n è 0, non limitiamo il numero di risultati
        limit_clause = "" if limit== 0 else f"LIMIT {limit}"

        # Costruisci la query in base a se `instrument_type` è vuoto o meno
        if instrument_type:
            query = f'''
                SELECT ticker, ticker_name, {percent_change_field}
                FROM json_data
                WHERE nation = ? AND instrument_type = ?
                ORDER BY {percent_change_field} DESC
                {limit_clause}
            '''
            self.cursor.execute(query, (nation, instrument_type))
        else:
            query = f'''
                SELECT ticker, ticker_name, {percent_change_field}
                FROM json_data
                WHERE nation = ?
                ORDER BY {percent_change_field} DESC
                {limit_clause}
            '''
            self.cursor.execute(query, (nation,))

        # Ottieni i risultati
        results = self.cursor.fetchall()

        # Stampa i risultati
        if results:
            a=1
            #print(
            #    f"Top {limit if limit > 0 else 'all'} tickers per {percent_change_field} in {nation} {instrument_type if instrument_type else ''}:")
            #for result in results:
             #   print(f"Ticker: {result[0]}, Nome: {result[1]}, {percent_change_field}: {result[2]}")
            return results
        else:
            print(f"Nessun risultato trovato per {nation} {instrument_type if instrument_type else ''}")
            return None



    def get_sorted_tickers_by_signal6(self, nation, instrument_type, secondary_key='scoring', additional_columns=None):
        """
        Ottieni un DataFrame di ticker per nazione e tipo di strumento, ordinati per `signal6` secondo l'ordine definito
        e una chiave secondaria. È possibile includere colonne aggiuntive dal database.

        Args:
            nation (str): La nazione dei ticker da filtrare.
            instrument_type (str): Il tipo di strumento dei ticker da filtrare.
            secondary_key (str): La colonna secondaria su cui ordinare (default 'scoring').
            additional_columns (list): Una lista di colonne aggiuntive da includere nel DataFrame (opzionale).

        Returns:
            pd.DataFrame: Un DataFrame ordinato per `signal6` e la chiave secondaria.
        """

        # Definisci l'ordine personalizzato per `signal6`
        signal6_order = {
            'Uptrend': 1, 'Uptrend*': 2, 'Uptrend-': 3, 'Uptrend--': 4, 'Uptrend---': 5,
            'wakeup2': 6, 'wakeup2*': 7, 'wakeup2-': 8, 'wakeup1': 9, 'wakeup-1': 10,
            'sleep1': 11, 'sleep2': 12,
            'Downtrend': 13, 'Downtrend*': 14, 'Downtrend_revSig+': 15, 'Downtrend_revSig++': 16,
            'Downtrend_revSig+++': 17
        }

        # Verifica se la chiave secondaria è valida
        valid_keys = ['scoring', 'percent_change_2', 'percent_change_5', 'percent_change_10', 'percent_change_30']
        if secondary_key not in valid_keys:
            raise ValueError(f"La chiave secondaria deve essere una delle seguenti: {', '.join(valid_keys)}")

        # Includi colonne aggiuntive, se specificate
        additional_columns = additional_columns if additional_columns else []
        columns_to_select = ['ticker', 'ticker_name', 'signal6', secondary_key] + additional_columns
        columns_to_select_str = ', '.join(columns_to_select)

        # Esegui la query per ottenere i ticker, `signal6`, e la colonna della chiave secondaria, più le colonne aggiuntive
        query = f'''
            SELECT {columns_to_select_str}
            FROM json_data
            WHERE nation = ? AND instrument_type = ?
        '''
        self.cursor.execute(query, (nation, instrument_type))
        results = self.cursor.fetchall()

        # Se non ci sono risultati, restituisci un DataFrame vuoto
        if not results:
            print(f"Nessun risultato trovato per {nation} e {instrument_type}")
            return pd.DataFrame()

        # Crea un DataFrame con i risultati
        df = pd.DataFrame(results, columns=['Ticker', 'Ticker_Name', 'Signal6', secondary_key] + additional_columns)

        # Mappa i valori di `signal6` al loro rank numerico, quelli non trovati verranno posti alla fine
        df['Signal6_Rank'] = df['Signal6'].map(signal6_order).fillna(float('inf'))

        # Ordina prima per `Signal6_Rank` e poi per la chiave secondaria
        df = df.sort_values(by=['Signal6_Rank', secondary_key], ascending=[True, False])

        # Rimuovi la colonna di ranking usata per l'ordinamento
        df = df.drop(columns=['Signal6_Rank'])
        print("Sono qui")
        #print(f"Restituiti {len(df)} ticker ordinati per `Signal6` e {secondary_key}.")

        return df



    def get_sorted_tickers_by_keys(self, nation, instrument_type, primary_key='scoring',
                                   secondary_key='percent_change_2', additional_columns=None, min_volume=0):
        """
        Ottieni un DataFrame di ticker per nazione e tipo di strumento, ordinati in base alla chiave primaria e secondaria,
        con la possibilità di includere colonne aggiuntive e filtrare in base al volume.

        Args:
            nation (str): La nazione dei ticker da filtrare.
            instrument_type (str): Il tipo di strumento dei ticker da filtrare.
            primary_key (str): La colonna principale su cui ordinare (default 'scoring').
            secondary_key (str): La colonna secondaria su cui ordinare (default 'percent_change_2').
            additional_columns (list): Colonne aggiuntive da includere nel DataFrame (opzionale).
            min_volume (int): Il volume minimo richiesto per includere i ticker nei risultati.

        Returns:
            pd.DataFrame: Un DataFrame ordinato per la chiave primaria e secondaria, con eventuali colonne aggiuntive e filtrato per volume.
        """
        # Mappa delle chiavi accettate per l'ordinamento
        valid_keys = ['scoring', 'percent_change_2', 'percent_change_5', 'percent_change_10', 'percent_change_30',
                      'macd', 'volume','signal3','adx']

        # Controlla se le chiavi passate sono valide
        if primary_key not in valid_keys or secondary_key not in valid_keys:
            raise ValueError(
                f"Le chiavi primarie o secondarie devono essere una delle seguenti: {', '.join(valid_keys)}")

        # Filtra le colonne aggiuntive rimuovendo quelle già presenti come chiave primaria o secondaria
        additional_columns = additional_columns if additional_columns else []
        additional_columns = [col for col in additional_columns if col not in {primary_key, secondary_key}]

        # Costruisci l'elenco delle colonne da selezionare, includendo volume una sola volta
        columns_to_select = ['ticker', 'ticker_name', primary_key, secondary_key] + additional_columns
        columns_to_select_str = ', '.join(columns_to_select)

        # Costruisci la query per filtrare anche in base al volume
        query = f'''
            SELECT {columns_to_select_str}
            FROM json_data
            WHERE nation = ? AND instrument_type = ? AND volume > ?
            ORDER BY {primary_key} DESC, {secondary_key} DESC
        '''

        # Esegui la query con il filtro sul volume
        self.cursor.execute(query, (nation, instrument_type, min_volume))
        results = self.cursor.fetchall()

        # Se non ci sono risultati, restituisci un DataFrame vuoto
        if not results:
            print(f"Nessun risultato trovato per {nation}, {instrument_type} con volume > {min_volume}")
            return pd.DataFrame()

        # Crea un DataFrame con i risultati
        df = pd.DataFrame(results,
                          columns=['Ticker', 'Ticker_Name', primary_key, secondary_key] + additional_columns)

        #print(f"Restituiti {len(df)} ticker ordinati per {primary_key}, {secondary_key} e volume > {min_volume}.")

        return df

    def get_signal_counts_and_ticker_lists(self, nation, instrument_type):
        # Query per selezionare i segnali, `ticker_name`, `volume`, `percent_change_2`, `signal6` e `scoring` dal database
        query = '''
            SELECT ticker, ticker_name, signal1, signal2, signal3, signal4, signal5, volume, percent_change_2, signal6, scoring
            FROM json_data
            WHERE nation = ? AND instrument_type = ? AND volume > 1000
            ORDER BY percent_change_2 DESC
        '''
        self.cursor.execute(query, (nation, instrument_type))
        results = self.cursor.fetchall()

        # Verifica che ci siano risultati
        if not results:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Converte i risultati in un DataFrame
        df = pd.DataFrame(results,
                          columns=['Ticker', 'Ticker_Name', 'S1', 'S2', 'S3', 'S4', 'S5', 'Volume', 'Percent_Change_2',
                                   'Signal6', 'Scoring'])

        # Converte i segnali in valori numerici per evitare errori di tipo
        df[['S1', 'S2', 'S3', 'S4', 'S5']] = df[['S1', 'S2', 'S3', 'S4', 'S5']].apply(pd.to_numeric, errors='coerce')

        # DataFrames per conteggiare le occorrenze di segnali 1 e -1
        df_count_1 = pd.DataFrame({
            'S1': (df['S1'] == 1).sum(),
            'S2': (df['S2'] >0).sum(),
            'S3': (df['S3'] >0).sum(),
            'S4': (df['S4'] == 1).sum(),
            'S5': (df['S5'] == 1).sum()
        }, index=[0])

        df_count_neg_1 = pd.DataFrame({
            'S1': (df['S1'] == -1).sum(),
            'S2': (df['S2'] == -1).sum(),
            'S3': (df['S3'] == -1).sum(),
            'S4': (df['S4'] == -1).sum(),
            'S5': (df['S5'] == -1).sum()
        }, index=[0])

        # DataFrames separati per i ticker e i nomi dei ticker con segnali 1
        df_tickers_1 = pd.DataFrame({
            'S1': ', '.join(df[df['S1'] == 1]['Ticker']),
            'S2': ', '.join(df[df['S2'] >0]['Ticker']),
            'S3': ', '.join(df[df['S3'] >0]['Ticker']),
            'S4': ', '.join(df[df['S4'] == 1]['Ticker']),
            'S5': ', '.join(df[df['S5'] == 1]['Ticker'])
        }, index=[0])

        df_ticker_names_1 = pd.DataFrame({
            'S1': ', '.join(df[df['S1'] == 1]['Ticker_Name']),
            'S2': ', '.join(df[df['S2']>0]['Ticker_Name']),
            'S3': ', '.join(df[df['S3']>0]['Ticker_Name']),
            'S4': ', '.join(df[df['S4'] == 1]['Ticker_Name']),
            'S5': ', '.join(df[df['S5'] == 1]['Ticker_Name'])
        }, index=[0])

        # DataFrames per volume, percentuale di variazione, signal6 e scoring per i segnali 1
        df_volumes_1 = pd.DataFrame({
            'S1': ', '.join(df[df['S1'] == 1]['Volume'].astype(str)),
            'S2': ', '.join(df[df['S2'] >0]['Volume'].astype(str)),
            'S3': ', '.join(df[df['S3'] >0]['Volume'].astype(str)),
            'S4': ', '.join(df[df['S4'] == 1]['Volume'].astype(str)),
            'S5': ', '.join(df[df['S5'] == 1]['Volume'].astype(str))
        }, index=[0])

        df_percent_change_2_1 = pd.DataFrame({
            'S1': ', '.join(df[df['S1'] == 1]['Percent_Change_2'].astype(str)),
            'S2': ', '.join(df[df['S2'] >0]['Percent_Change_2'].astype(str)),
            'S3': ', '.join(df[df['S3'] >0]['Percent_Change_2'].astype(str)),
            'S4': ', '.join(df[df['S4'] == 1]['Percent_Change_2'].astype(str)),
            'S5': ', '.join(df[df['S5'] == 1]['Percent_Change_2'].astype(str))
        }, index=[0])

        df_signal6_1 = pd.DataFrame({
            'S1': ', '.join(df[df['S1'] == 1]['Signal6']),
            'S2': ', '.join(df[df['S2'] >0]['Signal6']),
            'S3': ', '.join(df[df['S3']>0]['Signal6']),
            'S4': ', '.join(df[df['S4'] == 1]['Signal6']),
            'S5': ', '.join(df[df['S5'] == 1]['Signal6'])
        }, index=[0])

        df_scoring_1 = pd.DataFrame({
            'S1': ', '.join(df[df['S1'] == 1]['Scoring'].astype(str)),
            'S2': ', '.join(df[df['S2'] >0]['Scoring'].astype(str)),
            'S3': ', '.join(df[df['S3'] >0]['Scoring'].astype(str)),
            'S4': ', '.join(df[df['S4'] == 1]['Scoring'].astype(str)),
            'S5': ', '.join(df[df['S5'] == 1]['Scoring'].astype(str))
        }, index=[0])

        return (df_count_1, df_count_neg_1, df_tickers_1, df_ticker_names_1,
                df_volumes_1, df_percent_change_2_1, df_signal6_1, df_scoring_1)

    def search_tickers(self, search_terms, nation=None, instrument_type=None):
        """
        Search tickers based on one or more strings (terms).

        Args:
            search_terms (list): A list of search strings.
            nation (str): Optional filter by nation.
            instrument_type (str): Optional filter by instrument type.

        Returns:
            pd.DataFrame: A DataFrame of tickers matching the search terms.
        """
        query = "SELECT * FROM json_data WHERE " + " OR ".join([f"ticker_name LIKE ?"] * len(search_terms))
        params = [f"%{term}%" for term in search_terms]

        if nation:
            query += " AND nation = ?"
            params.append(nation)

        if instrument_type:
            query += " AND instrument_type = ?"
            params.append(instrument_type)

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        if results:
            columns = [description[0] for description in self.cursor.description]
            return pd.DataFrame(results, columns=columns)
        else:
            print("No results found.")
            return pd.DataFrame()


    def save_json_data(self, json_data_str, nation, instrument_type):
        # Converte la stringa JSON in un dizionario
        json_data = json.loads(json_data_str)

        # Estrai i dati dal JSON
        ticker = json_data['ticker']
        ticker_name = json_data['ticker_name']
        signals = json_data['signals'][0]  # Assume che ci sia almeno un elemento nei signals

        # Rimuovi campi duplicati nel signals (Ticker, Ticker Name)
        signals.pop('Ticker', None)
        signals.pop('Ticker Name', None)

        # Estrai i pattern CDL (quelli diversi da zero)
        cdl_patterns = {key: value for key, value in signals.items() if key.startswith('CDL') and value != 0}
        cdl_patterns_str = ', '.join([f"{key}={value}" for key, value in cdl_patterns.items()])

        # Calcola il `Scoring` come somma dei trend_indicator1, 2, 3, 4
        scoring = sum([int(signals.get(f'TrendIndicator{i}', 0) or 0) for i in range(1, 5)])

        # Aggiungi valori mancanti se il JSON non contiene tutte le colonne
        fields = [
            'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Percent_Change_2', 'Percent_Change_5',
            'Percent_Change_10', 'Percent_Change_30', 'EMA_50', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'MACD_Prev', 'MACD_Signal_Prev', 'RSI', 'SAR', 'ADX', '+DX', '-DX', 'Stochastic_K', 'Stochastic_D',
            'Stochastic_K_Prev', 'Stochastic_D_Prev', 'Alligator_Jaw', 'Alligator_Teeth', 'Alligator_Lips',
            'ATR', 'ATR_Trailing_Stop_Loss', 'Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower', 'MFI', 'Date',
            'TrendIndicator1', 'TrendIndicator2', 'TrendIndicator3', 'TrendIndicator4', 'Signal1', 'Signal2',
            'Signal3', 'Signal4', 'Signal5', 'Signal6'
        ]

        # Garantire che ogni valore mancante sia sostituito con None
        for field in fields:
            if field not in signals:
                signals[field] = None

        # Valori per l'inserimento nel DB, inclusa la nuova colonna `scoring`
        columns = [
            'ticker', 'ticker_name', 'nation', 'instrument_type', 'open', 'high', 'low', 'close', 'adj_close', 'volume',
            'percent_change_2', 'percent_change_5', 'percent_change_10', 'percent_change_30', 'ema_50', 'macd',
            'macd_signal', 'macd_histogram', 'macd_prev', 'macd_signal_prev', 'rsi', 'sar', 'adx', 'plus_dx', 'minus_dx',
            'stochastic_k', 'stochastic_d', 'stochastic_k_prev', 'stochastic_d_prev', 'alligator_jaw', 'alligator_teeth',
            'alligator_lips', 'atr', 'atr_trailing_stop_loss', 'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
            'mfi', 'date', 'trend_indicator1', 'trend_indicator2', 'trend_indicator3', 'trend_indicator4', 'scoring',
            'signal1', 'signal2', 'signal3', 'signal4', 'signal5', 'signal6', 'cdl_patterns'
        ]

        values = [
            ticker, ticker_name, nation, instrument_type, signals['Open'], signals['High'], signals['Low'],
            signals['Close'], signals['Adj Close'], signals['Volume'], signals['Percent_Change_2'],
            signals['Percent_Change_5'], signals['Percent_Change_10'], signals['Percent_Change_30'], signals['EMA_50'],
            signals['MACD'], signals['MACD_Signal'], signals['MACD_Histogram'], signals['MACD_Prev'],
            signals['MACD_Signal_Prev'], signals['RSI'], signals['SAR'], signals['ADX'], signals['+DX'], signals['-DX'],
            signals['Stochastic_K'], signals['Stochastic_D'], signals['Stochastic_K_Prev'], signals['Stochastic_D_Prev'],
            signals['Alligator_Jaw'], signals['Alligator_Teeth'], signals['Alligator_Lips'], signals['ATR'],
            signals['ATR_Trailing_Stop_Loss'], signals['Bollinger_Upper'], signals['Bollinger_Middle'],
            signals['Bollinger_Lower'], signals['MFI'], signals['Date'], signals['TrendIndicator1'], signals['TrendIndicator2'],
            signals['TrendIndicator3'], signals['TrendIndicator4'], scoring, signals['Signal1'], signals['Signal2'],
            signals['Signal3'], signals['Signal4'], signals['Signal5'], signals['Signal6'], cdl_patterns_str
        ]

        # Sostituisci eventuali None con 'NULL' per evitare errori SQLite
        values = ['NULL' if v is None else v for v in values]

        # Inserisci o aggiorna i dati nelle rispettive colonne del database
        self.cursor.execute(f'''
            INSERT OR REPLACE INTO json_data (
                {", ".join(columns)}
            ) VALUES ({", ".join(["?"] * len(columns))})
        ''', values)

        self.conn.commit()

'''
myDb=dbTickersData()
jj=myDb.load_json_data("LALU.MI")
print(jj)
df_count_1, df_count_neg_1, df_tickers_1, df_ticker_names_1,df_volume, df_percent_change_2, df_signal6, df_scoring = myDb.get_signal_counts_and_ticker_lists("IT","ETC")
print(df_count_1.to_string())
print(df_tickers_1.to_string())


myDb=dbTickersData()
ticker_data = myDb.get_sorted_tickers_by_keys("IT", 'ETC', "scoring","percent_change_2",
                                            ["volume", "signal6", "percent_change_2", "scoring"], min_volume=1500)

# Assicurati che 'scoring' e 'percent_change_2' siano trattati come numeri (float)
ticker_data['scoring'] = pd.to_numeric(ticker_data['scoring'], errors='coerce')
ticker_data['percent_change_2'] = pd.to_numeric(ticker_data['percent_change_2'], errors='coerce')

# Ordina prima per 'scoring' (decrescente) e poi per 'percent_change_2' (decrescente)
ticker_data_sorted = ticker_data.sort_values(by=['scoring', 'percent_change_2'], ascending=[False, False])

# Verifica i primi risultati
print(ticker_data_sorted.to_string())

# Puoi restituire ticker_data_sorted, o utilizzarlo come necessario


print(myDb.load_json_data("COCO.MI"))

print(myDb.search_signal3_greater_than_zero())
print(myDb.get_top_n_tickers_by_percent_change("IT","ETC",2,10))
print(myDb.get_top_n_tickers_by_percent_change("IT","ETF",2,10))
print(myDb.get_top_n_tickers_by_percent_change("IT","MIB30",2,10))
print(myDb.get_signal_counts_and_ticker_lists("IT","ETC"))
print(myDb.get_sorted_tickers_by_signal6("IT","ETC",'scoring',['RSI','Volume']).to_string())
print(myDb.get_sorted_tickers_by_keys("IT","ETC","scoring","adx",['RSI'],1500))'''

