import streamlit as st
from page_login import login_page
from page_portfolio import portfolio_page
from page_watchlist import page_watchlist
from page_ticker_summary import page_ticker_summary  # Importa la nuova pagina
from page_insights import page_insights
from page_signals import page_signals
from page_alligator import page_alligator
#st.set_page_config(page_title="Applicazione Portafogli", layout="centered", page_icon="📊")


#gestionelink
page = st.session_state.get("query_params", {}).get("page", "login")
# Debugging: mostra lo stato corrente della sessione
print("---------enterin webMAin ----")
print("Session State(!):", st.session_state)
print("Pagina selezionata:", page)




# Imposta la pagina corrente basata sul session state o URL
page = st.session_state.get("query_params", {}).get("page", "login")

# Gestione del routing
if page == "login":
    login_page()
elif page == "portfolio":
    portfolio_page()
elif page == "watchlist":
    page_watchlist()
elif page == "ticker_summary":  # Nuova pagina per i dettagli del ticker
    page_ticker_summary()
elif page == "insights":  # Nuova pagina per i dettagli del ticker
    page_insights()
elif page == "signals":  # Nuova pagina per i dettagli del ticker
    page_signals()
elif page == "alligator":
    page_alligator()

else:
    st.error("Pagina non trovata.")
