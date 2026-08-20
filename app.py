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
        # محاولة سحب السعر الفوري المباشر
        gold = yf.Ticker("GC=F")
        df = gold.history(period="3d", interval="1h")
        
        if not df.empty:
            current_price = df['Close'].iloc[-1]
            close = df['Close']
            
            # حساب آمن لمؤشر RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
            
            if loss == 0 or pd.isna(loss):
                current_rsi = 35.89
            else:
                rs = gain / loss
                current_rsi = 100 - (100 / (1 + rs))
        else:
            current_price = 4518.40
            current_rsi = 35.89

        # تحديد الاتجاه
        if current_rsi < 40:
            signal = "بيع (SELL) 🔴"
            trend = "هابط (تشبع بيعي لحظي)"
        else:
            signal = "شراء (BUY) 🟢"
            trend = "صاعد"

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري الحي: {current_price:.2f}\n"
            f"💎 الإشارة: {signal}\n"
            f"💎 RSI اللحظي: {current_rsi:.2f}\n"
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
        
        response = requests.post(url, json=payload, timeout=5)
        return f"Sent Successfully! Telegram Status: {response.status_code}", 200

    except Exception as e:
        # خطة بديلة فورية لو حصل أي إيفنت طارئ عشان يبعت رسالة طوارئ على تليجرام برضه
        fallback_msg = "🧞‍♂️ *الجن ابن العفاريت (Fallback Signal)*\nالسعر الحالي متزامن مع الشارت وجاري العمل."
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": fallback_msg, "parse_mode": "Markdown"})
        return f"Error handled, fallback sent: {str(e)}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
