class User:
    def __init__(self, firstname: str, lastname: str, email: str, password: str, role: str = "user", note: str = ""):
        """
        Inizializza un'istanza della classe User.

        :param firstname: Nome dell'utente.
        :param lastname: Cognome dell'utente.
        :param email: Email dell'utente.
        :param password: Password dell'utente.
        :param role: Ruolo dell'utente (es. admin, user). Default: "user".
        :param note: Note aggiuntive sull'utente.
        """
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = self._encrypt_password(password)
        self.role = role
        self.note = note

    def _encrypt_password(self, password: str) -> str:
        """
        Cifra la password dell'utente per la sicurezza.
        In un contesto reale, utilizza librerie come bcrypt o hashlib.

        :param password: Password in chiaro da cifrare.
        :return: Password cifrata (stringa).
        """
        # Esempio semplice di cifratura (da sostituire con una libreria di sicurezza come bcrypt)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def update_email(self, new_email: str):
        """
        Aggiorna l'indirizzo email dell'utente.

        :param new_email: Nuovo indirizzo email.
        """
        self.email = new_email

    def update_role(self, new_role: str):
        """
        Aggiorna il ruolo dell'utente.

        :param new_role: Nuovo ruolo dell'utente (es. admin, user).
        """
        self.role = new_role

    def update_note(self, new_note: str):
        """
        Aggiorna le note associate all'utente.

        :param new_note: Nuova nota.
        """
        self.note = new_note

    def to_dict(self) -> dict:
        """
        Converte l'istanza utente in un dizionario.

        :return: Dizionario con le informazioni dell'utente.
        """
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "role": self.role,
            "note": self.note
        }

    def __repr__(self):
        """
        Rappresentazione stringa dell'istanza dell'utente.

        :return: Stringa con le informazioni dell'utente.
        """
        return (f"User(firstname='{self.firstname}', lastname='{self.lastname}', "
                f"email='{self.email}', role='{self.role}', note='{self.note}')")
