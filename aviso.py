import pandas as pd
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = "587"
EMAIL_USERNAME = "miguelvieiradatascience@gmail.com"
EMAIL_PASSWORD = "adzw fflv yzmk jwix"
EMAIL_TO = "miguelvmesquitads@gmail.com"


# Caminho do arquivo CSV
CSV_FILE = "dados_formulario.csv"
CHECK_INTERVAL = 10  # Intervalo de verificação em segundos
PREVIOUS_LINE_COUNT_FILE = "line_count.txt"

def send_email(new_rows):
    """Envia um e-mail quando há novas linhas no CSV."""
    subject = "Novo Registro no Formulário"
    body = f"Novos dados foram adicionados ao formulário:\n\n{new_rows.to_string(index=False)}"
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USERNAME
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, EMAIL_TO, msg.as_string())
        print("📧 E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

def get_previous_line_count():
    """Lê a quantidade de linhas do CSV que já foram processadas anteriormente."""
    if os.path.exists(PREVIOUS_LINE_COUNT_FILE):
        with open(PREVIOUS_LINE_COUNT_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def update_line_count(count):
    """Atualiza o número de linhas processadas no arquivo de controle."""
    with open(PREVIOUS_LINE_COUNT_FILE, "w") as f:
        f.write(str(count))

def monitor_csv():
    """Monitora o CSV e envia e-mails ao detectar novas linhas."""
    previous_line_count = get_previous_line_count()

    while True:
        try:
            df = pd.read_csv(CSV_FILE)
            current_line_count = len(df)

            if current_line_count > previous_line_count:
                new_rows = df.iloc[previous_line_count:]  # Novas linhas adicionadas
                send_email(new_rows)
                update_line_count(current_line_count)

            previous_line_count = current_line_count
        except Exception as e:
            print(f"❌ Erro ao ler o CSV: {e}")

        time.sleep(CHECK_INTERVAL)  # Espera antes de verificar novamente

# 🔹 Iniciar o monitoramento (executa infinitamente)
if __name__ == "__main__":
    monitor_csv()

