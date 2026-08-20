import os
import time
import requests
from flask import Flask

app = Flask(__name__)

# استدعاء التوكن والتشات آي دي من إعدادات رندر
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_gold_price():
    """سحب السعر الفوري بأمان تام"""
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
    """إرسال رسالة لتليجرام"""
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
        return f"XAUUSD Bot is Live! Current Gold Price: {price}"
    return "XAUUSD Bot is Running, connecting to market..."

# تشغيل لوب خلفي آمن وخفيف جداً
import threading

def background_loop():
    # ننتظر دقيقة لحد ما السيرفر يقوم تماماً
    time.sleep(60)
    while True:
        try:
            price = get_gold_price()
            if price:
                # حسابات ذكية مبسطة وآمنة تماماً
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
                send_telegram_message(msg)
        except Exception as e:
            print(f"Loop error: {e}")
        
        # النوم لمدة 15 دقيقة
        time.sleep(900)

# تشغيل الخيط في الخلفية بأمان
thread = threading.Thread(target=background_loop, daemon=True)
thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
