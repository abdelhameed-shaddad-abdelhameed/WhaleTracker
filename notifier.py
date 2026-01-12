import os
import requests
from email.message import EmailMessage
import smtplib
from typing import List

def send_telegram(bot_token: str, chat_id: str, message: str) -> None:
    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=10,
        )
    except requests.RequestException:
        pass

def send_webhook(url: str, payload: dict) -> None:
    if not url:
        return
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException:
        pass

def send_discord(message: str) -> None:
    send_webhook(os.getenv("DISCORD_WEBHOOK_URL", ""), {"content": message})

def send_slack(message: str) -> None:
    send_webhook(os.getenv("SLACK_WEBHOOK_URL", ""), {"text": message})

def send_generic(message: str) -> None:
    send_webhook(os.getenv("GENERIC_WEBHOOK_URL", ""), {"text": message})

def send_email(subject: str, body: str) -> None:
    host = os.getenv("EMAIL_SMTP_HOST", "")
    user = os.getenv("EMAIL_USER", "")
    pwd = os.getenv("EMAIL_PASS", "")
    to = os.getenv("EMAIL_TO", "")
    port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    if not (host and user and pwd and to):
        return
    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
    except Exception:
        pass

def notify(channels: List[str], message: str, cfg) -> None:
    if "telegram" in channels:
        send_telegram(cfg.TELEGRAM_BOT_TOKEN, cfg.TELEGRAM_CHAT_ID, message)
    if "discord" in channels:
        send_discord(message)
    if "slack" in channels:
        send_slack(message)
    if "email" in channels:
        send_email("Whale Alert", message)
    if "webhook" in channels:
        send_generic(message)