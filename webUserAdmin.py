import streamlit as st
import pandas as pd
from dbUsers import dbUsers
from User import User

# Inizializzazione dell'oggetto dbUsers
db = dbUsers()

# Impostazioni di Streamlit
st.set_page_config(page_title="Gestione Utenti", layout="centered")

# Titolo della pagina
st.title("Gestione Utenti")

# Sezione per la creazione di un nuovo utente
st.header("Crea un nuovo utente")

with st.form(key='user_form'):
    firstname = st.text_input("Nome")
    lastname = st.text_input("Cognome")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Ruolo", ["user", "admin"])
    note = st.text_area("Note")

    # Pulsante per l'invio del modulo
    submit_button = st.form_submit_button("Crea Utente")

    if submit_button:
        # Creazione di un nuovo utente e inserimento nel database
        if firstname and lastname and email and password:
            new_user = User(firstname=firstname, lastname=lastname, email=email, password=password, role=role, note=note)
            db.insert_user(new_user)
            st.success(f"Utente {firstname} {lastname} creato con successo!")
        else:
            st.error("Compila tutti i campi obbligatori!")

# Sezione per visualizzare gli utenti esistenti
st.header("Lista Utenti")

# Visualizzazione degli utenti nel database
users = db.get_all_users()
if users:
    user_df = pd.DataFrame(users, columns=["Nome", "Cognome", "Email", "Password", "Ruolo", "Note"])
    st.dataframe(user_df)

    # Selezione dell'utente per modifiche o cancellazioni
    selected_email = st.selectbox("Seleziona l'email dell'utente da modificare o cancellare", [user[2] for user in users])

    # Selezione della nuova azione da eseguire
    action = st.selectbox("Azione", ["Aggiorna Ruolo", "Elimina Utente"])

    if action == "Aggiorna Ruolo":
        new_role = st.selectbox("Nuovo Ruolo", ["user", "admin"])
        if st.button("Aggiorna Ruolo"):
            db.update_user_role(selected_email, new_role)
            st.success(f"Ruolo dell'utente con email {selected_email} aggiornato con successo.")

    elif action == "Elimina Utente":
        if st.button("Elimina Utente"):
            db.delete_user(selected_email)
            st.success(f"Utente con email {selected_email} eliminato con successo.")
else:
    st.write("Nessun utente presente nel database.")
