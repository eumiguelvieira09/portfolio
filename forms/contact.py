import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import streamlit as st
import requests
import pandas as pd
import os
from aviso import send_email
import aviso

# Nome do arquivo CSV para armazenar os dados localmente
CSV_FILE = "dados_formulario.csv"

WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

def is_valid_email(email):
    """Valida se o email fornecido é válido."""
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email) is not None

def save_to_csv(name, email, message):
    """Salva os dados do formulário em um arquivo CSV local."""
    new_data = pd.DataFrame([{"Nome": name, "Email": email, "Mensagem": message}])

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
        send_email
    else:
        df = new_data

    df.to_csv(CSV_FILE, index=False)

def contact_form():
    with st.form("contact_form"):
        name = st.text_input("First Name")
        email = st.text_input("Email Address")
        message = st.text_area("Your Message")
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        send_email
        if not WEBHOOK_URL:
            st.error("Email service is not set up. Please try again later.", icon="📧")
            st.stop()

        if not name:
            st.error("Please provide your name.", icon="🧑")
            st.stop()

        if not email:
            st.error("Please provide your email address.", icon="📨")
            st.stop()

        if not is_valid_email(email):
            st.error("Please provide a valid email address.", icon="📧")
            st.stop()

        if not message:
            st.error("Please provide a message.", icon="💬")
            st.stop()

        # Salvar os dados no CSV

        # Salvar os dados no CSV
        save_to_csv(name, email, message)

        # Enviar e-mail imediatamente com os dados recém-preenchidos
        send_email(pd.DataFrame([{"Nome": name, "Email": email, "Mensagem": message}]))


        # Enviar os dados para um webhook (ex: Zapier, API externa)
        data = {"email": email, "name": name, "message": message}
        response = requests.post(WEBHOOK_URL, json=data)

        if response.status_code == 200:
            st.success("Your message has been sent successfully! 🎉", icon="🚀")
            
        else:
            st.success("Your message has been sent successfully!", icon="🚀")
