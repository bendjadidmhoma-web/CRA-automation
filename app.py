import os
import re
import base64
import requests
import subprocess
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MAIL_TO = os.getenv("MAIL_TO")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

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

    match = re.search(r"CRA\s+(\d+)\s+(\d+)\s+(\d+)", text, re.IGNORECASE)

    if not match:
        send_telegram(chat_id, "Format attendu : CRA 20 6 2026")
        return "ok"

    nb_jours = match.group(1)
    mois = int(match.group(2))
    annee = int(match.group(3))

    mois_noms = {
        1: "Janvier",
        2: "Fevrier",
        3: "Mars",
        4: "Avril",
        5: "Mai",
        6: "Juin",
        7: "Juillet",
        8: "Aout",
        9: "Septembre",
        10: "Octobre",
        11: "Novembre",
        12: "Decembre"
    }

    subprocess.run([
        "python",
        "generer_cra_v3.py",
        "--mois", str(mois),
        "--annee", str(annee),
        "--nb-jours", str(nb_jours)
    ], check=True)

    pdf_filename = f"CRA_{mois_noms[mois]}_{annee}.pdf"

    envoyer_mail(
        subject=f"CRA {mois_noms[mois]} {annee}",
        body=f"Bonjour,\n\nVeuillez trouver ci-joint mon CRA de {mois_noms[mois]} {annee}, avec {nb_jours} jours.\n\nCordialement,\nMHOMA Ben Djadid",
        attachment_path=pdf_filename
    )

    send_telegram(chat_id, f"CRA envoyé ✅ ({nb_jours} jours - {mois_noms[mois]} {annee})")

    return "ok"

def send_telegram(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

def envoyer_mail(subject, body, attachment_path):
    with open(attachment_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode("utf-8")

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "onboarding@resend.dev",
            "to": MAIL_TO,
            "subject": subject,
            "text": body,
            "attachments": [
                {
                    "filename": attachment_path,
                    "content": file_data
                }
            ]
        }
    )

    if response.status_code >= 400:
        raise Exception(f"Erreur Resend: {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)