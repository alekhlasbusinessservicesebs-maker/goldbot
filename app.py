import os
from flask import Flask
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

# متغير لحفظ السعر السابق عشان نقارن بيه الاتجاه
last_price = 0.0

def send_signal():
    global last_price
    try:
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        if response.status_code != 200:
            return
            
        data = response.json()
        current_price = float(data.get('price', 2500.00))
        
        # لو دي أول مرة، نعتبر السعر السابق هو الحالي
        if last_price == 0.0:
            last_price = current_price

        # مقارنة السعر الحالي بالسابق لتحديد الاتجاه الفعلي للشارت
        if current_price >= last_price:
            signal = "شراء (STRONG BUY) 🟢"
            trend = "صاعد (Momentum Up)"
            tp1 = current_price + 3.00
            tp2 = current_price + 6.00
            tp3 = current_price + 10.00
            sl = current_price - 4.00
        else:
            signal = "بيع (STRONG SELL) 🔴"
            trend = "هابط (Momentum Down)"
            tp1 = current_price - 3.00
            tp2 = current_price - 6.00
            tp3 = current_price - 10.00
            sl = current_price + 4.00

        # تحديث السعر السابق للدورة القادمة
        last_price = current_price

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP (Live Trend)* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري الحي: `{current_price:.2f}`\n"
            f"💎 نوع الإشارة: {signal}\n"
            f"💎 نقطة الدخول: `{current_price:.2f}`\n"
            f"💎 الاتجاه اللحظي: {trend}\n\n"
            f"🎯 *الأهداف (TP):*\n"
            f"• *TP1:* `{tp1:.2f}`\n"
            f"• *TP2:* `{tp2:.2f}`\n"
            f"• *TP3:* `{tp3:.2f}`\n\n"
            f"🛑 *وقف الخسارة (SL):* `{sl:.2f}`\n"
            f"---------------------------\n"
            f"⚙️ *تحليل الزخم اللحظي الحقيقي*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error: {e}")

@app.route('/')
def home():
    send_signal()
    return "Gold Bot is Live and Running!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
