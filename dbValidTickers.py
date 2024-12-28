# file: dbValidTickers.py

import os
import sqlite3
import pandas as pd


class dbValidTickers:
    def __init__(self, db_path="/home/developer/PycharmProjects/learningProjects/IFinance/valid_tickers.db"):
        """
        Inizializza la connessione al database e crea la tabella `valid_tickers` se non esiste.

        :param db_path: Percorso del database SQLite. Default: 'valid_tickers.db'.
        """
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()
        self.create_table()

    def update_excluded(self, ticker_id, excluded_value):
        """
        Aggiorna il valore del campo 'Excluded' per un dato ticker.

        :param ticker_id: ID del ticker nel database.
        :param excluded_value: Nuovo valore per il campo 'Excluded' (0 o 1).
        """
        self.c.execute('''
            UPDATE valid_tickers
            SET excluded = ?
            WHERE id = ?
        ''', (excluded_value, ticker_id))
        self.conn.commit()
        print(f"Ticker con ID {ticker_id} aggiornato con il valore 'Excluded' = {excluded_value}.")

    def create_table(self):
        """
        Crea la tabella `valid_tickers` nel database se non esiste.
        """
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS valid_tickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                name TEXT,
                nation TEXT,
                instrument_type TEXT,
                excluded INTEGER DEFAULT 0  -- Campo per escludere i ticker (0 = non escluso, 1 = escluso)
            )
        ''')
        self.conn.commit()

    def get_tickers_by_nation_and_instrument(db, nation, instrument_type):
        """
        Restituisce una lista di ticker e nomi ticker filtrati per nazione e tipo di strumento.

        :param db: L'istanza della classe dbValidTickers.
        :param nation: La nazione da filtrare.
        :param instrument_type: Il tipo di strumento da filtrare.
        :return: DataFrame con colonne 'Ticker' e 'Name' che corrispondono ai filtri.
        """
        query = '''
            SELECT ticker, name ,excluded
            FROM valid_tickers
            WHERE nation = ? AND instrument_type = ?
        '''
        df = pd.read_sql_query(query, db.conn, params=(nation, instrument_type))
        return df

    def get_tickers_by_instrument(self, instrument_type):
        """
        Restituisce i ticker filtrati in base al tipo di strumento specificato (ETC, ETF o MIB30).

        :param instrument_type: Il tipo di strumento da filtrare (ETC, ETF o MIB30).
        :return: DataFrame contenente i ticker filtrati.
        """
        query = '''
            SELECT * FROM valid_tickers
            WHERE instrument_type = ?
        '''
        df = pd.read_sql_query(query, self.conn, params=(instrument_type,))
        return df

    def ticker_exists(self, ticker, nation, instrument_type):
        """
        Controlla se un ticker esiste già nel database con la stessa nazione e tipo di strumento.

        :param ticker: Ticker da verificare.
        :param nation: Nazione del ticker.
        :param instrument_type: Tipo di strumento del ticker.
        :return: True se il ticker esiste già, False altrimenti.
        """
        self.c.execute('''
            SELECT COUNT(*) FROM valid_tickers
            WHERE ticker = ? AND nation = ? AND instrument_type = ?
        ''', (ticker, nation, instrument_type))
        count = self.c.fetchone()[0]
        return count > 0

    def import_from_file(self, file_path):
        """
        Importa i ticker da un file Excel e li inserisce nella tabella `valid_tickers` se non esistono già.

        :param file_path: Percorso del file Excel.
        """
        try:
            # Legge il file in un DataFrame
            df = pd.read_excel(file_path)
            if 'Ticker' in df.columns and 'Name' in df.columns:
                # Estrae la nazione e il tipo di strumento dal nome del file
                file_name = os.path.basename(file_path)
                parts = file_name.split('_')
                nation = parts[1]
                instrument_type = parts[2].split('.')[0]  # Estrae solo la parte prima dell'estensione

                # Inserisce i dati nel database se non esistono già
                for _, row in df.iterrows():
                    #ticker = row['Ticker']
                    #name = row['Name']
                    ticker = row['Ticker'].replace(" ", "")
                    name = row['Name'].replace(" ", "")

                    # Controlla se il ticker esiste già per la combinazione (ticker, nation, instrument_type)
                    if not self.ticker_exists(ticker, nation, instrument_type):
                        self.c.execute('''
                            INSERT INTO valid_tickers (ticker, name, nation, instrument_type)
                            VALUES (?, ?, ?, ?)
                        ''', (ticker, name, nation, instrument_type))
                        print(f"Ticker {ticker} inserito nel database.")
                    else:
                        print(
                            f"Ticker {ticker} già presente nel database con la combinazione nazione '{nation}' e tipo di strumento '{instrument_type}'.")
                self.conn.commit()
                print(f"Dati importati con successo da {file_name}")
            else:
                print(f"Errore: Il file {file_path} non contiene le colonne richieste ('Ticker' e 'Name').")
        except Exception as e:
            print(f"Errore durante l'importazione: {e}")

    def get_all_tickers(self):
        """
        Restituisce tutti i ticker presenti nel database.

        :return: Lista di ticker dal database.
        """
        self.c.execute('SELECT * FROM valid_tickers')
        return self.c.fetchall()

    def delete_market(self, nation=None, instrument_type=None):
        """
        Cancella i ticker in base alla nazione e/o al tipo di strumento.

        :param nation: La nazione dei ticker da cancellare (opzionale).
        :param instrument_type: Il tipo di strumento dei ticker da cancellare (opzionale).
        """
        query = 'DELETE FROM valid_tickers WHERE 1=1'  # Condizione base sempre vera
        params = []

        if nation:
            query += ' AND nation = ?'
            params.append(nation)

        if instrument_type:
            query += ' AND instrument_type = ?'
            params.append(instrument_type)

        self.c.execute(query, params)
        self.conn.commit()
        print(f"Mercato {nation} e tipo di strumento {instrument_type} cancellati con successo.")

    def __del__(self):
        """
        Chiude la connessione al database quando l'istanza viene eliminata.
        """
        self.conn.close()

    def add_ticker(self, ticker, name, nation, instrument_type):
        """
        Aggiunge un nuovo ticker al database.

        Args:
            self: Riferimento all'istanza della classe.
            ticker: Simbolo del ticker.
            name: Nome completo del titolo.
            nation: Nazione di provenienza.
            instrument_type: Tipo di strumento finanziario.
        """

        # Controlliamo se il ticker esiste già
        if self.ticker_exists(ticker, nation, instrument_type):
            print(
                f"Il ticker {ticker} esiste già per la combinazione nazione '{nation}' e tipo di strumento '{instrument_type}'.")
            return

        # Inseriamo il nuovo ticker nel database
        self.c.execute('''
            INSERT INTO valid_tickers (ticker, name, nation, instrument_type)
            VALUES (?, ?, ?, ?)
        ''', (ticker, name, nation, instrument_type))
        self.conn.commit()
        print(f"Ticker {ticker} aggiunto con successo.")
