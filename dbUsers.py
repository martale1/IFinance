import sqlite3
from User import User

class dbUsers:
    def __init__(self, db_path='users.db'):
        """
        Inizializza la connessione al database e crea la tabella `users` se non esiste.

        :param db_path: Percorso del database SQLite. Default: 'users.db'.
        """
        self.conn = sqlite3.connect(db_path,check_same_thread=False)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Crea la tabella `users` nel database se non esiste.
        """
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                firstname TEXT,
                lastname TEXT,
                email TEXT PRIMARY KEY,
                password TEXT,
                role TEXT,
                note TEXT
            )
        ''')
        self.conn.commit()

    def insert_user(self, user: User):
        """
        Inserisce un nuovo utente nel database.

        :param user: Istanza della classe User da inserire.
        """
        try:
            self.c.execute('''
                INSERT INTO users (firstname, lastname, email, password, role, note)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user.firstname, user.lastname, user.email, user.password, user.role, user.note))
            self.conn.commit()
            print(f"Utente {user.firstname} {user.lastname} inserito con successo nel database.")
        except sqlite3.IntegrityError:
            print(f"Errore: L'utente con email {user.email} esiste già nel database.")

    def get_all_users(self):
        """
        Restituisce una lista di tutti gli utenti presenti nel database.

        :return: Lista di tuple contenenti le informazioni degli utenti.
        """
        self.c.execute('SELECT * FROM users')
        return self.c.fetchall()

    def update_user_role(self, email: str, new_role: str):
        """
        Aggiorna il ruolo di un utente in base all'email.

        :param email: Email dell'utente da aggiornare.
        :param new_role: Nuovo ruolo da assegnare all'utente.
        """
        self.c.execute('''
            UPDATE users
            SET role = ?
            WHERE email = ?
        ''', (new_role, email))
        self.conn.commit()
        print(f"Ruolo dell'utente con email {email} aggiornato a {new_role}.")

    def delete_user(self, email: str):
        """
        Elimina un utente dal database in base all'email.

        :param email: Email dell'utente da eliminare.
        """
        self.c.execute('''
            DELETE FROM users
            WHERE email = ?
        ''', (email,))
        self.conn.commit()
        print(f"Utente con email {email} eliminato dal database.")

    def get_user(self, email: str):
        """
        Restituisce le informazioni di un utente specifico in base all'email.

        :param email: Email dell'utente da cercare.
        :return: Una tupla con le informazioni dell'utente.
        """
        self.c.execute('''
            SELECT * FROM users
            WHERE email = ?
        ''', (email,))
        return self.c.fetchone()

    def __del__(self):
        """
        Chiude la connessione al database quando l'istanza viene eliminata.
        """
        self.conn.close()
