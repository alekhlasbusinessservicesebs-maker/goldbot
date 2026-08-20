import os
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

@app.route("/")
def home():
    try:
        url = "https://www.gold-api.com/api/XAU/USD"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = float(data.get("price") or data.get("ask") or 0)
            
            # تجهيز الرسالة
            sl = price - 4.5
            tp1 = price + 4.0
            tp2 = price + 8.0
            
            msg = (
                f"🚨 *XAUUSD SIGNAL* 🚨\n\n"
                f"🟡 *السعر الحالي:* `{price:.2f}`\n"
                f"📊 *الاتجاه:* `STRONG BUY / صاعد`\n\n"
                f"🎯 *الأهداف:* \n"
                f"🔹 TP1: `{tp1:.2f}`\n"
                f"🔹 TP2: `{tp2:.2f}`\n\n"
                f"🛑 *وقف الخسارة:* `{sl:.2f}`"
            )
            
            # إرسال الرسالة لتليجرام فوراً
            send_telegram_message(msg)
            return f"Bot is Live & Signal Sent! Gold Price: {price}"
            
    except Exception as e:
        return f"Error: {e}"
        
    return "Bot is running..."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
