import requests

# Telegram Bot Config
TELEGRAM_BOT_TOKEN = '7577725465:AAHP3BYJZmiVI2HUJhZMKlOVdXpW42hHhJ0'
TELEGRAM_CHAT_ID = '-4901397732'

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'  # optional: for formatting
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram send error: {e}")

