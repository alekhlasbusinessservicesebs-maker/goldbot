import os
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

@app.route('/')
def home():
    try:
        # رسالة إشارة الذهب المباشرة
        message = (
            f"🔥 *Mody Luck Gold System (Live)* 🔥\n"
            f"---------------------------\n"
            f"💎 السعر الفوري: 4456.25\n"
            f"💎 نوع الإشارة: بيع SELL 🔴\n"
            f"---------------------------\n"
            f"🎯 الأهداف (TP): 4452.75, 4449.25\n"
            f"🛡 حماية (SL): 4460.75\n"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            return "Telegram Message Sent Successfully!", 200
        else:
            return f"Telegram API Error: {response.text}", 200

    except Exception as e:
        return f"Error: {str(e)}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
