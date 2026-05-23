# CRA Telegram App

Application Render gratuite : Telegram -> génération CRA PDF -> envoi Gmail.

## Commande Render

Build Command :
```bash
pip install -r requirements.txt
```

Start Command :
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

## Variables Render

- TELEGRAM_BOT_TOKEN : token donné par BotFather
- MAIL_FROM : ton adresse Gmail
- MAIL_PASSWORD : mot de passe d'application Gmail
- MAIL_TO : destinataire du CRA
- ALLOWED_CHAT_ID : optionnel, ton chat id Telegram

## Webhook Telegram

Après déploiement, ouvrir dans le navigateur :

```text
https://api.telegram.org/botTON_TOKEN/setWebhook?url=https://TON-URL-RENDER.onrender.com/telegram
```

## Messages Telegram

```text
CRA 21
```

ou :

```text
CRA 21 5 2026
```
