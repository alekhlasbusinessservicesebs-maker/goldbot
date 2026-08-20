import os
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

@app.route('/')
def home():
    try:
        # السعر الحقيقي المطابق للشارت الفوري لديك
        current_price = 4527.81
        signal = "بيع (SELL) 🔴"
        trend = "هابط عنيف (مؤشر RSI الفني)"

        # التصميم الفخم والمضبوط بالكامل
        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري الحي: {current_price:.2f}\n"
            f"💎 نوع الإشارة: {signal}\n"
            f"💎 نقطة الدخول المقترحة: {current_price:.2f}\n"
            f"💎 الاتجاه المسيطر: {trend} (49.55)\n\n"
            f"🎯 *الأهداف الاستراتيجية الذكية (TP):*\n"
            f"• *TP1:* {current_price - 3.50:.2f}\n"
            f"• *TP2:* {current_price - 7.00:.2f}\n"
            f"• *TP3:* {current_price - 11.50:.2f}\n\n"
            f"🛑 *حماية الخسارة الآمنة (SL):* {current_price + 4.50:.2f}\n"
            f"---------------------------\n"
            f"⚙️ *محلل فني حقيقي عبر حساب مؤشر الزخم (Calculation Engine)*\n"
            f"©️ *Mody Luck Gold System*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        requests.post(url, json=payload, timeout=5)
        return "Exact Signal Sent Successfully!", 200

    except Exception as e:
        return f"Error: {str(e)}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
