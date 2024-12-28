import sqlite3

class dbWatchlist:
    def __init__(self, db_path='watchlist.db'):
        """
        Inizializza la connessione al database e crea la tabella `watchlist` se non esiste.

        :param db_path: Percorso del database SQLite. Default: 'watchlist.db'.
        """
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Crea la tabella `watchlist` nel database se non esiste.
        """
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                watchlist_name TEXT,
                ticker_symbol TEXT,
                UNIQUE(user_email, watchlist_name, ticker_symbol),  -- Vincolo per evitare duplicati
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        self.conn.commit()

    def create_watchlist(self, user_email: str, watchlist_name: str):
        """
        Crea una nuova watchlist per l'utente specificato.

        :param user_email: Email dell'utente proprietario della watchlist.
        :param watchlist_name: Nome della watchlist da creare.
        """
        try:
            self.c.execute('''
                INSERT INTO watchlist (user_email, watchlist_name)
                VALUES (?, ?)
            ''', (user_email, watchlist_name))
            self.conn.commit()
            print(f"Watchlist '{watchlist_name}' creata con successo per l'utente {user_email}.")
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Errore durante la creazione della watchlist: {e}")

    def add_ticker_to_watchlist(self, watchlist_name: str, user_email: str, ticker_symbol: str):
        """
        Aggiunge un ticker a una watchlist esistente.

        :param watchlist_name: Nome della watchlist a cui aggiungere il ticker.
        :param user_email: Email dell'utente proprietario della watchlist.
        :param ticker_symbol: Simbolo del ticker da aggiungere.
        """
        try:
            # Verifica che il ticker non sia già presente nella watchlist
            self.c.execute('''
                SELECT * FROM watchlist
                WHERE user_email = ? AND watchlist_name = ? AND ticker_symbol = ?
            ''', (user_email, watchlist_name, ticker_symbol))
            if self.c.fetchone():
                raise ValueError(f"Il ticker {ticker_symbol} è già presente nella watchlist '{watchlist_name}'.")

            # Inserisce il ticker nella watchlist (non specificare la colonna `id` che è AUTOINCREMENT)
            self.c.execute('''
                INSERT INTO watchlist (user_email, watchlist_name, ticker_symbol)
                VALUES (?, ?, ?)
            ''', (user_email, watchlist_name, ticker_symbol))
            self.conn.commit()
            print(f"Ticker {ticker_symbol} aggiunto con successo alla watchlist '{watchlist_name}'.")
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Errore nell'aggiunta del ticker: {e}")

    def get_watchlists(self, user_email: str):
        """
        Ottiene tutte le watchlist associate a un utente specifico.

        :param user_email: Email dell'utente di cui ottenere le watchlist.
        :return: Lista di tuple contenenti le informazioni delle watchlist.
        """
        self.c.execute('''
            SELECT DISTINCT watchlist_name FROM watchlist
            WHERE user_email = ?
        ''', (user_email,))
        return self.c.fetchall()

    def get_tickers_in_watchlist(self, user_email: str, watchlist_name: str):
        """
        Ottiene tutti i ticker presenti in una watchlist specifica.

        :param user_email: Email dell'utente di cui ottenere i ticker nella watchlist.
        :param watchlist_name: Nome della watchlist di cui ottenere i ticker.
        :return: Lista di ticker presenti nella watchlist.
        """
        self.c.execute('''
            SELECT ticker_symbol FROM watchlist
            WHERE user_email = ? AND watchlist_name = ?
        ''', (user_email, watchlist_name))
        return self.c.fetchall()

    def delete_watchlist(self, watchlist_name: str, user_email: str):
        """
        Elimina una watchlist specifica dal database.

        :param watchlist_name: Nome della watchlist da eliminare.
        :param user_email: Email dell'utente di cui eliminare la watchlist.
        """
        try:
            self.c.execute('''
                DELETE FROM watchlist
                WHERE user_email = ? AND watchlist_name = ?
            ''', (user_email, watchlist_name))
            self.conn.commit()
            print(f"Watchlist '{watchlist_name}' eliminata con successo.")
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Errore nell'eliminazione della watchlist: {e}")

    def delete_ticker_from_watchlist(self, user_email: str, watchlist_name: str, ticker_symbol: str):
        """
        Rimuove un ticker da una watchlist specifica.

        :param user_email: Email dell'utente di cui eliminare il ticker.
        :param watchlist_name: Nome della watchlist da cui rimuovere il ticker.
        :param ticker_symbol: Simbolo del ticker da rimuovere.
        """
        try:
            self.c.execute('''
                DELETE FROM watchlist
                WHERE user_email = ? AND watchlist_name = ? AND ticker_symbol = ?
            ''', (user_email, watchlist_name, ticker_symbol))
            self.conn.commit()
            print(f"Ticker {ticker_symbol} rimosso con successo dalla watchlist '{watchlist_name}'.")
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Errore nella rimozione del ticker dalla watchlist: {e}")

    def __del__(self):
        """
        Chiude la connessione al database quando l'istanza viene eliminata.
        """
        self.conn.close()
