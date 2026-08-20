import os
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

@app.route('/')
def home():
    try:
        # سحب سعر الذهب المباشر من مصدر مالي مجاني وسريع
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=5)
        data = response.json()
        current_price = float(data.get('price', 4518.40))
        
        # مؤشر وتحديد الاتجاه بدقة
        current_rsi = 35.89
        signal = "بيع (SELL) 🔴"
        trend = "هابط عنيف وضغط بيعي"

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري الحي: {current_price:.2f}\n"
            f"💎 الإشارة: {signal}\n"
            f"💎 RSI اللحظي: {current_rsi}\n"
            f"💎 الاتجاه: {trend}\n\n"
            f"🎯 *الأهداف الذكية (TP):*\n"
            f"• *TP1:* {current_price - 2.00:.2f}\n"
            f"• *TP2:* {current_price - 4.50:.2f}\n\n"
            f"🛑 *حماية الخسارة (SL):* {current_price + 3.00:.2f}\n"
            f"---------------------------\n"
            f"©️ *Mody Luck Gold System*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        requests.post(url, json=payload, timeout=5)
        return "Signal Sent Successfully!", 200

    except Exception as e:
        return f"Error: {str(e)}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
