import os
import requests
import yfinance as yf
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAElReV2Tv2j2xTpmYR6IGDeo5UTQqTsB1k"
CHAT_ID = "5760283457"

@app.route('/')
def home():
    try:
        # سحب سعر الذهب الفوري
        gold = yf.Ticker("GC=F")
        data = gold.history(period="2d", interval="1h")
        
        if data.empty:
            return "No data found", 400

        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        
        diff = current_price - prev_price
        signal = "شراء BUY 🟢" if diff >= 0 else "بيع SELL 🔴"

        message = (
            f"🔥 *Mody Luck Gold System (Live)* 🔥\n"
            f"---------------------------\n"
            f"💎 السعر الفوري: {current_price:.2f}\n"
            f"💎 نوع الإشارة: {signal}\n"
            f"---------------------------\n"
            f"🎯 الأهداف (TP): {current_price+5:.2f}, {current_price+10:.2f}\n"
            f"🛡 حماية (SL): {current_price-3:.2f}\n"
        )

        # إرسال رسالة تليجرام عبر الـ API المباشر بدون مشاكل Async
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return "Signal Sent Successfully via HTTP API!"
        else:
            return f"Telegram Error: {response.text}", 400

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
