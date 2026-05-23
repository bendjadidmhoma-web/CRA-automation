import os
import re
import smtplib
from email.message import EmailMessage
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
MAIL_TO = os.getenv("MAIL_TO")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/")
def home():
    return "CRA Bot OK ✅"

@app.route("/set-webhook")
def set_webhook():
    render_url = request.host_url.rstrip("/")
    webhook_url = f"{render_url}/webhook"

    r = requests.get(
        f"{TELEGRAM_API}/setWebhook",
        params={"url": webhook_url}
    )

    return r.text

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    match = re.search(r"CRA\s+(\d+)", text, re.IGNORECASE)

    if not match:
        send_telegram(chat_id, "Format attendu : CRA 20")
        return "ok"

    nb_jours = match.group(1)

    sujet = "CRA automatique"
    contenu = f"CRA généré avec {nb_jours} jours."

    envoyer_mail(sujet, contenu)

    send_telegram(chat_id, f"CRA envoyé ✅ ({nb_jours} jours)")

    return "ok"

def send_telegram(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

def envoyer_mail(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = MAIL_TO
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)