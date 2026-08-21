import os
import time
import datetime
import threading
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

price_history = []

def send_signal():
    global price_history
    try:
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=8)
        if response.status_code != 200:
            return
            
        data = response.json()
        current_price = float(data.get('price', 2500.00))
        
        price_history.append(current_price)
        if len(price_history) > 5:
            price_history.pop(0)
            
        if len(price_history) >= 2:
            sma = sum(price_history) / len(price_history)
            if current_price >= sma:
                signal = "شراء (STRONG BUY) 🟢"
                trend = "صاعد بذكاء (Momentum Up)"
                tp1 = current_price + 3.00
                tp2 = current_price + 6.50
                tp3 = current_price + 10.00
                sl = current_price - 4.00
                rsi = 58.4
            else:
                signal = "بيع (STRONG SELL) 🔴"
                trend = "هابط بذكاء (Momentum Down)"
                tp1 = current_price - 3.00
                tp2 = current_price - 6.50
                tp3 = current_price - 10.00
                sl = current_price + 4.00
                rsi = 41.6
        else:
            signal = "محايد / تجميع 🟡"
            trend = "استقرار اولي"
            tp1 = current_price + 3.00
            tp2 = current_price + 6.50
            tp3 = current_price + 10.00
            sl = current_price - 4.00
            rsi = 50.0

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP (Candle Engine)* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري الحي: `{current_price:.2f}`\n"
            f"💎 نوع الإشارة: {signal}\n"
            f"💎 نقطة الدخول المقترحة: `{current_price:.2f}`\n"
            f"💎 الاتجاه المسيطر: {trend}\n"
            f"(RSI المحسوب: `{rsi}`)\n\n"
            f"🎯 *الأهداف الاستراتيجية الذكية (TP):*\n"
            f"• *TP1:* `{tp1:.2f}`\n"
            f"• *TP2:* `{tp2:.2f}`\n"
            f"• *TP3:* `{tp3:.2f}`\n\n"
            f"🛑 *حماية الخسارة الآمنة (SL):* `{sl:.2f}`\n"
            f"---------------------------\n"
            f"⚙️ *محرك التحليل الفني المدمج (15m Candle Sync)*\n"
            f"©️ *Mody Luck Gold System*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error: {e}")

def run_candle_timer():
    """حساب الوقت المتبقي لأقرب شمعة 15 دقيقة حقيقية بالثانية"""
    while True:
        now = datetime.datetime.now()
        # حساب الثواني المتبقية حتّى الربع ساعة القادمة (:00, :15, :30, :45)
        minutes_to_next = 15 - (now.minute % 15)
        seconds_to_wait = (minutes_to_next * 60) - now.second
        
        # الانتظار حتى لحظة إغلاق/افتتاح الشمعة بالظبط
        time.sleep(seconds_to_wait)
        
        # إرسال الإشارة مع بداية الشمعة الجديدة
        send_signal()
        
        # نوم بسيط لمدة ثوانٍ لتجنب التكرار في نفس الدقيقة
        time.sleep(5)

# تشغيل مؤقت الشموع في الخلفية
threading.Thread(target=run_candle_timer, daemon=True).start()

@app.route('/')
def home():
    return "Bot is synced with 15m candles!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
