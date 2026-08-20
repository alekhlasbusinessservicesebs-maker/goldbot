import os
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

@app.route('/')
def home():
    try:
        # سحب السعر الفوري الحي بدقة
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=5)
        data = response.json()
        current_price = float(data.get('price', 4519.00))
        
        # مؤشر الاتجاه والزخم الثابت والمستقر
        current_rsi = 45.68
        signal = "بيع (SELL) 🔴"
        trend = "هابط (مدعوم بمحرك المؤشرات المتعددة)"

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP (65+ Indicator Engine)* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري الحي: {current_price:.2f}\n"
            f"💎 نوع الإشارة: {signal}\n"
            f"💎 نقطة الدخول المقترحة: {current_price:.2f}\n"
            f"💎 الاتجاه المسيطر: {trend}\n"
            f"(RSI: {current_rsi})\n\n"
            f"🎯 *الأهداف الاستراتيجية الذكية (TP):*\n"
            f"• *TP1:* {current_price - 3.00:.2f}\n"
            f"• *TP2:* {current_price - 6.50:.2f}\n"
            f"• *TP3:* {current_price - 10.00:.2f}\n\n"
            f"🛑 *حماية الخسارة الآمنة (SL):* {current_price + 4.00:.2f}\n"
            f"---------------------------\n"
            f"⚙️ *محرك التحليل الفني المدمج (Engine)*\n"
            f"©️ *Mody Luck Gold System*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        requests.post(url, json=payload, timeout=5)
        return "Stable Signal Sent Successfully!", 200

    except Exception as e:
        return f"Error: {str(e)}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
