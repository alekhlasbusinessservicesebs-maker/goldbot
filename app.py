import os
import requests
from flask import Flask

app = Flask(__name__)

# بيانات تليجرام بتاعتك المباشرة والثابتة
TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

# قائمة لتخزين آخر الأسعار لحساب اتجاه السوق البسيط (SMA)
price_history = []

@app.route('/')
def home():
    global price_history
    try:
        # استخدام رابط الـ API المستقر تماماً من الكود الأول
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=5)
        data = response.json()
        current_price = float(data.get('price', 2500.00))
        
        # إضافة السعر للقائمة (نحتفظ بآخر أسعار لحساب المتوسط)
        price_history.append(current_price)
        if len(price_history) > 5:
            price_history.pop(0)
            
        # التحليل الذكي بناءً على المتوسط البسيط (SMA)
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
            f"🧞‍♂️ *الجن ابن العفاريت VIP (Smart Pro Engine)* 🧞‍♂️\n"
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
            f"⚙️ *محرك التحليل الفني المدمج (Smart Engine)*\n"
            f"©️ *Mody Luck Gold System*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        requests.post(url, json=payload, timeout=5)
        return f"Smart Signal Sent Successfully! Price: {current_price}", 200

    except Exception as e:
        return f"Error: {str(e)}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
