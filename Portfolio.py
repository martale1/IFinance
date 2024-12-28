from User import User
from Ticker import Ticker
from User import User
from Ticker import Ticker

class Portfolio:
    def __init__(self, user: User, name: str):
        """
        Inizializza un'istanza del portafoglio associata a un utente.

        :param user: Istanza della classe User a cui è associato il portafoglio.
        :param name: Nome del portafoglio.
        """
        self.user = user
        self.name = name
        self.holdings = []  # Lista vuota per contenere gli strumenti finanziari con dettagli sui ticker

    def add_holding(self, strumento: str, valuta: str, quantita: str, prezzo_medio_carico: str, ticker: Ticker):
        """
        Aggiunge un nuovo strumento finanziario al portafoglio con un oggetto Ticker associato.
        Utilizza il campo `close` del Ticker come prezzo di mercato.

        :param strumento: Tipo di strumento (es. ETF, ETC).
        :param valuta: Valuta di riferimento (es. Euro, Dollari).
        :param quantita: Quantità posseduta.
        :param prezzo_medio_carico: Prezzo medio di acquisto.
        :param ticker: Istanza della classe Ticker associata allo strumento.
        """
        prezzo_mercato = ticker.close  # Utilizza il prezzo di chiusura del Ticker come prezzo di mercato
        holding = {
            "strumento": strumento,
            "valuta": valuta,
            "quantita": quantita,
            "prezzo_medio_carico": prezzo_medio_carico,
            "prezzo_mercato": prezzo_mercato,
            "variazione_percentuale": "0",  # Inizialmente la variazione è 0, verrà calcolata dopo
            "ticker": ticker  # Associa l'oggetto ticker a questo strumento
        }
        self.holdings.append(holding)
        print(f"Strumento {strumento} con ticker {ticker.ticker} aggiunto al portafoglio {self.name} di {self.user.firstname}.")

    def remove_holding(self, strumento: str):
        """
        Rimuove uno strumento finanziario dal portafoglio in base al nome dello strumento.

        :param strumento: Nome dello strumento da rimuovere.
        """
        self.holdings = [holding for holding in self.holdings if holding["strumento"] != strumento]
        print(f"Strumento {strumento} rimosso dal portafoglio {self.name} di {self.user.firstname}.")

    def list_holdings(self):
        """
        Visualizza tutti gli strumenti finanziari presenti nel portafoglio.
        """
        if not self.holdings:
            print(f"Nessun strumento presente nel portafoglio {self.name} di {self.user.firstname}.")
        else:
            print(f"Strumenti nel portafoglio {self.name} di {self.user.firstname}:")
            for holding in self.holdings:
                ticker = holding['ticker']
                print(f"- {holding['strumento']} (Quantità: {holding['quantita']}, Prezzo Medio: {holding['prezzo_medio_carico']}, "
                      f"Prezzo di Mercato: {holding['prezzo_mercato']}, Variazione: {holding['variazione_percentuale']}%, "
                      f"Ticker: {ticker.ticker} - {ticker.ticker_name})")

    def calculate_variation(self):
        """
        Calcola la variazione percentuale per ciascun strumento nel portafoglio e la aggiorna nel dizionario degli strumenti.
        La variazione percentuale viene calcolata in base al prezzo medio di carico e al prezzo di mercato del Ticker.
        """
        for holding in self.holdings:
            try:
                prezzo_medio = float(holding["prezzo_medio_carico"])
                prezzo_mercato = float(holding["prezzo_mercato"])
                variazione = ((prezzo_mercato - prezzo_medio) / prezzo_medio) * 100
                holding["variazione_percentuale"] = f"{variazione:.2f}"
            except ValueError:
                print(f"Errore nel calcolo della variazione per lo strumento {holding['strumento']}. Controlla i valori di prezzo.")

    def to_dict(self) -> dict:
        """
        Converte il portafoglio in un dizionario, includendo gli strumenti e i dettagli dei ticker.

        :return: Dizionario del portafoglio.
        """
        return {
            "user": {
                "firstname": self.user.firstname,
                "lastname": self.user.lastname,
                "email": self.user.email,
                "role": self.user.role
            },
            "portfolio_name": self.name,
            "holdings": [
                {
                    "strumento": holding["strumento"],
                    "valuta": holding["valuta"],
                    "quantita": holding["quantita"],
                    "prezzo_medio_carico": holding["prezzo_medio_carico"],
                    "prezzo_mercato": holding["prezzo_mercato"],
                    "variazione_percentuale": holding["variazione_percentuale"],
                    "ticker": holding["ticker"].to_dict()  # Converte il ticker associato in un dizionario
                }
                for holding in self.holdings
            ]
        }

    def __repr__(self):
        """
        Rappresentazione stringa dell'istanza del portafoglio per il debug.

        :return: Stringa con le informazioni principali del portafoglio.
        """
        return f"Portfolio({self.name}, Owner: {self.user.firstname} {self.user.lastname}, Holdings: {len(self.holdings)})"



'''
user_antonino = User(firstname="Antonino", lastname="Rossi", email="antonino.rossi@example.com", password="securepassword")

# Creazione e popolamento di un Ticker
ticker_aapl = Ticker(ticker="AAPL")
ticker_aapl.populate_fields_from_analyzer(period='2y')
ticker_vod = Ticker(ticker="VOD.L")
ticker_vod.populate_fields_from_analyzer(period='2y')
# Creazione di un portafoglio per l'utente Antonino
portfolio = Portfolio(user=user_antonino, name="Portafoglio Principale di Antonino")

# Aggiungiamo strumenti finanziari al portafoglio utilizzando il Ticker
portfolio.add_holding(strumento="ETF", valuta="Euro", quantita="100", prezzo_medio_carico="50.0", ticker=ticker_aapl)
portfolio.add_holding(strumento="ETF", valuta="Euro", quantita="100", prezzo_medio_carico="50.0", ticker=ticker_vod)

# Visualizziamo gli strumenti nel portafoglio
portfolio.list_holdings()

# Calcoliamo la variazione percentuale per ciascuno strumento
portfolio.calculate_variation()

# Visualizziamo nuovamente gli strumenti con le variazioni calcolate
portfolio.list_holdings()

# Convertiamo il portafoglio in dizionario e stampiamolo
portfolio_dict = portfolio.to_dict()
print("\nDizionario del portafoglio:")
print(portfolio_dict)
'''