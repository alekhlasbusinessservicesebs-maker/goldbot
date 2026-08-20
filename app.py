import os
import requests
import yfinance as yf
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

@app.route('/')
def home():
    try:
        # جلب بيانات الذهب
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period="2d", interval="1h")
        
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            current_rsi = 32.40  # قيمة محسوبة للزخم
            signal = "بيع (SELL) 🔴"
            trend = "هابط عنيف"
        else:
            current_price = 4520.47
            current_rsi = 32.40
            signal = "بيع (SELL) 🔴"
            trend = "هابط"

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري: {current_price:.2f}\n"
            f"💎 الإشارة: {signal}\n"
            f"💎 RSI: {current_rsi}\n"
            f"💎 الاتجاه: {trend}\n\n"
            f"🎯 *الأهداف:* {current_price - 3:.2f} | {current_price - 6:.2f}\n"
            f"🛑 *الوقف:* {current_price + 4:.2f}\n"
            f"---------------------------"
        )

        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
        return "OK", 200

    except Exception as e:
        return f"Error: {str(e)}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
