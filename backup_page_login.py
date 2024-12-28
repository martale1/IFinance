import streamlit as st
from dbUsers import dbUsers
from User import User
from messaging import messaging

def login_page():
    # Inizializzazione della classe dbUsers
    db_users = dbUsers()

    # Impostazioni della pagina (Chiamala solo se non è già stata chiamata in `main_app.py`)
    st.title("Login:")


    # Campi di input per il login
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = db_users.get_user(login_email)
        if user and user[3] == User._encrypt_password(None, login_password):  # Confronta la password cifrata
            if (user[0])!="mau":
                ms = messaging()
                ms.send("User connected:"+user[0])
            #st.success("Cookie impostato!")
            st.success(f"Benvenuto, {user[0]} {user[1]}!")
            # Imposta l'email dell'utente nella sessione
            st.session_state["user_email"] = login_email
            # Reindirizza alla pagina di gestione del portafoglio
            st.session_state.query_params = {"page": "insights"}
            #st.experimental_rerun()  # Ricarica la pagina con i nuovi parametri
            st.rerun()
        else:
            st.error("Wrong Email of Password.")
