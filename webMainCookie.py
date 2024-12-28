import streamlit as st
from page_login import login_page
from page_portfolio import portfolio_page
from page_watchlist import page_watchlist
from page_ticker_summary import page_ticker_summary
from page_insights import page_insights
from streamlit_cookies_manager import EncryptedCookieManager

# Configurazione del cookie manager
cookies = EncryptedCookieManager(prefix="example/", password="my_secret_password")
if not cookies.ready():
    st.stop()  # Aspetta che i cookies siano pronti

# Controlla se il cookie è impostato e valido
if "my_cookie" in cookies and cookies["my_cookie"] == "cookie_user_connected":
    page = st.session_state.get("query_params", {}).get("page", "insights")
    print(page)
else:
    # Usa `page` da `session_state` o imposta "login" come predefinito
    page = st.session_state.get("query_params", {}).get("page", "login")

# Debugging: mostra lo stato corrente della sessione
print("---------enterin webMain ----")
print("Session State(!):", st.session_state)
print("Pagina selezionata:", page)

# Gestione del routing
if page == "login":
    login_page()
elif page == "portfolio":
    portfolio_page()
elif page == "watchlist":
    page_watchlist()
elif page == "ticker_summary":
    page_ticker_summary()
elif page == "insights":
    page_insights()
else:
    st.error("Pagina non trovata.")
