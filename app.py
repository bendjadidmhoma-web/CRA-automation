import os
import re
import smtplib
import subprocess
import sys
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import requests
from flask import Flask, request

BASE_DIR = Path(__file__).resolve().parent
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_ID = os.environ.get("ALLOWED_CHAT_ID", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_TO = os.environ.get("MAIL_TO", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

app = Flask(__name__)

MOIS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
    7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}


def send_telegram_message(chat_id: str, text: str):
    if not BOT_TOKEN:
        return
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=20,
    )


def send_email_with_pdf(pdf_path: Path, mois: int, annee: int, nb_jours: str):
    if not all([MAIL_FROM, MAIL_PASSWORD, MAIL_TO]):
        raise RuntimeError("Variables mail manquantes : MAIL_FROM, MAIL_PASSWORD, MAIL_TO")

    mois_nom = MOIS_FR[mois]
    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg["Subject"] = f"CRA {mois_nom} {annee} - MHOMA Ben Djadid"
    msg.set_content(
        f"Bonjour,\n\nVeuillez trouver ci-joint mon CRA du mois de {mois_nom} {annee}.\n\n"
        f"Nombre de jours déclarés : {nb_jours}\n\nCordialement,\nMHOMA Ben Djadid"
    )

    with pdf_path.open("rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=pdf_path.name)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(MAIL_FROM, MAIL_PASSWORD)
        smtp.send_message(msg)


def parse_message(text: str):
    # Formats acceptés : "CRA 21" ou "CRA 21 5 2026"
    match = re.search(r"^\s*CRA\s+(\d+(?:[\.,]\d+)?)\s*(?:(\d{1,2})\s+(\d{4}))?\s*$", text, re.I)
    if not match:
        return None
    nb_jours = match.group(1).replace(",", ".")
    now = datetime.now()
    mois = int(match.group(2)) if match.group(2) else now.month
    annee = int(match.group(3)) if match.group(3) else now.year
    if mois < 1 or mois > 12:
        raise ValueError("Le mois doit être entre 1 et 12")
    return nb_jours, mois, annee


@app.get("/health")
def health():
    return "ok"


@app.post("/telegram")
def telegram_webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))
    text = message.get("text", "")

    if not chat_id or not text:
        return "ignored", 200

    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        send_telegram_message(chat_id, "Accès refusé.")
        return "forbidden", 200

    try:
        parsed = parse_message(text)
        if not parsed:
            send_telegram_message(chat_id, "Format attendu : CRA 21 ou CRA 21 5 2026")
            return "bad format", 200

        nb_jours, mois, annee = parsed
        output = Path("/tmp") / f"CRA_{MOIS_FR[mois]}_{annee}.pdf"

        subprocess.run(
            [
                sys.executable,
                str(BASE_DIR / "generer_cra_v3.py"),
                "--mois", str(mois),
                "--annee", str(annee),
                "--nb-jours", str(nb_jours),
                "--template", str(BASE_DIR / "Modele_CRA_sans_mois_tableau_conserve.pdf"),
                "--sortie", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        send_email_with_pdf(output, mois, annee, nb_jours)
        send_telegram_message(chat_id, f"CRA {MOIS_FR[mois]} {annee} envoyé ✅ ({nb_jours} jours)")
        return "ok", 200

    except Exception as e:
        send_telegram_message(chat_id, f"Erreur CRA ❌ : {e}")
        return "error", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
