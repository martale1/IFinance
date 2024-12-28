import sqlite3
from Ticker import Ticker

class dbPortfolio:
    def __init__(self, db_path='portfolio.db'):
        """
        Inizializza la connessione al database e crea la tabella `portfolios` se non esiste.

        :param db_path: Percorso del database SQLite. Default: 'portfolio.db'.
        """
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Crea le tabelle `portfolios` e `portfolio_tickers` nel database se non esistono.
        """
        # Tabella che associa i portafogli agli utenti
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                portfolio_name TEXT,
                FOREIGN KEY(user_email) REFERENCES users(email)
            )
        ''')

        # Tabella che memorizza i ticker in ciascun portafoglio
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_tickers (
                portfolio_id INTEGER,
                ticker TEXT,
                quantita TEXT,
                prezzo_medio_carico TEXT,
                prezzo_mercato TEXT,
                variazione_percentuale TEXT,
                FOREIGN KEY(portfolio_id) REFERENCES portfolios(portfolio_id)
            )
        ''')
        self.conn.commit()



    def delete_ticker_from_portfolio(self, portfolio_id: int, ticker: str):
        """
        Rimuove un ticker specifico da un portafoglio.

        :param portfolio_id: ID del portafoglio dal quale rimuovere il ticker.
        :param ticker: Nome del ticker da rimuovere.
        """
        self.c.execute('''
            DELETE FROM portfolio_tickers
            WHERE portfolio_id = ? AND ticker = ?
        ''', (portfolio_id, ticker))
        self.conn.commit()  # Corretto con parentesi per eseguire la commit
        print(f"Ticker {ticker} rimosso con successo dal portafoglio con ID {portfolio_id}.")


    def create_portfolio(self, user_email: str, portfolio_name: str):
        """
        Crea un nuovo portafoglio associato a un utente.

        :param user_email: Email dell'utente proprietario del portafoglio.
        :param portfolio_name: Nome del portafoglio da creare.
        """
        self.c.execute('''
            INSERT INTO portfolios (user_email, portfolio_name)
            VALUES (?, ?)
        ''', (user_email, portfolio_name))
        self.conn.commit()
        print(f"Portafoglio '{portfolio_name}' creato con successo per l'utente {user_email}.")

    def get_portfolios(self, user_email: str):
        """
        Restituisce tutti i portafogli associati a un utente.

        :param user_email: Email dell'utente.
        :return: Lista di portafogli dell'utente.
        """
        self.c.execute('''
            SELECT portfolio_id, portfolio_name
            FROM portfolios
            WHERE user_email = ?
        ''', (user_email,))
        return self.c.fetchall()

    def add_ticker_to_portfolio(self, portfolio_id: int, ticker: Ticker, quantita: str, prezzo_medio_carico: str):
        """
        Aggiunge un ticker a un portafoglio specifico.

        :param portfolio_id: ID del portafoglio a cui aggiungere il ticker.
        :param ticker: Istanza della classe Ticker da aggiungere.
        :param quantita: Quantità del ticker nel portafoglio.
        :param prezzo_medio_carico: Prezzo medio di carico.
        """
        prezzo_mercato = ticker.close  # Utilizza il campo `close` del ticker come prezzo di mercato
        variazione_percentuale = str(((float(prezzo_mercato) - float(prezzo_medio_carico)) / float(prezzo_medio_carico)) * 100)

        self.c.execute('''
            INSERT INTO portfolio_tickers (portfolio_id, ticker, quantita, prezzo_medio_carico, prezzo_mercato, variazione_percentuale)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (portfolio_id, ticker.ticker, quantita, prezzo_medio_carico, prezzo_mercato, variazione_percentuale))
        self.conn.commit()
        print(f"Ticker {ticker.ticker} aggiunto al portafoglio con ID {portfolio_id}.")

    def get_tickers_in_portfolio(self, portfolio_id: int):
        """
        Restituisce tutti i ticker presenti in un portafoglio specifico.

        :param portfolio_id: ID del portafoglio.
        :return: Lista di ticker nel portafoglio.
        """
        self.c.execute('''
            SELECT ticker, quantita, prezzo_medio_carico, prezzo_mercato, variazione_percentuale
            FROM portfolio_tickers
            WHERE portfolio_id = ?
        ''', (portfolio_id,))
        return self.c.fetchall()

    def delete_portfolio(self, portfolio_id: int):
        """
        Elimina un portafoglio e tutti i ticker associati.

        :param portfolio_id: ID del portafoglio da eliminare.
        """
        # Elimina i ticker associati al portafoglio
        self.c.execute('DELETE FROM portfolio_tickers WHERE portfolio_id = ?', (portfolio_id,))
        # Elimina il portafoglio
        self.c.execute('DELETE FROM portfolios WHERE portfolio_id = ?', (portfolio_id,))
        self.conn.commit()
        print(f"Portafoglio con ID {portfolio_id} eliminato con successo.")

    def __del__(self):
        """
        Chiude la connessione al database quando l'istanza viene eliminata.
        """
        self.conn.close()
