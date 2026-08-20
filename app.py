import os
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_gold_price():
    try:
        url = "https://www.gold-api.com/api/XAU/USD"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("price") or data.get("ask") or 0)
    except Exception as e:
        print(f"API Error: {e}")
    return None

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
    price = get_gold_price()
    if price:
        # حسابات الأهداف البسيطة
        sl = price - 4.5
        tp1 = price + 4.0
        tp2 = price + 8.0
        
        msg = (
            f"🚨 *XAUUSD SIGNAL (Smart Free)* 🚨\n\n"
            f"🟡 *السعر الحالي:* `{price:.2f}`\n"
            f"📊 *الاتجاه:* `STRONG BUY / صاعد`\n\n"
            f"🎯 *الأهداف:* \n"
            f"🔹 TP1: `{tp1:.2f}`\n"
            f"🔹 TP2: `{tp2:.2f}`\n\n"
            f"🛑 *وقف الخسارة:* `{sl:.2f}`"
        )
        
        # إرسال الرسالة فوراً عند زيارة الرابط
        send_telegram_message(msg)
        return f"Signal Sent Successfully! Current Gold Price: {price}"
        
    return "Bot is running, but couldn't fetch price right now."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
