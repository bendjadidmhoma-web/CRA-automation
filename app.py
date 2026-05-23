from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "CRA Bot OK ✅"

@app.route("/set-webhook")
def webhook():
    return "Webhook configuré ✅"