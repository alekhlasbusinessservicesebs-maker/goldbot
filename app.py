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
        # سحب السعر الفوري للذهب XAUUSD من المصدر الحقيقي
        ticker = yf.Ticker("XAUUSD=X")
        data = ticker.history(period="1d", interval="1m")
        
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            
            # حساب RSI الحقيقي برمجياً (مش وهمي)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # تحديد الاتجاه بناءً على RSI الحقيقي
            if current_rsi < 35:
                signal = "بيع (SELL) 🔴"
                trend = "هابط (تشبع بيعي)"
            elif current_rsi > 65:
                signal = "شراء (BUY) 🟢"
                trend = "صاعد (تشبع شرائي)"
            else:
                signal = "انتظار (WAIT) 🟡"
                trend = "عرضي (تذبذب)"
        else:
            return "Data Fetch Error", 500

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت (Live Market Data)* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الحي: {current_price:.2f}\n"
            f"💎 الإشارة: {signal}\n"
            f"💎 RSI: {current_rsi:.2f}\n"
            f"💎 الاتجاه: {trend}\n\n"
            f"🎯 *الأهداف:* {current_price - 2:.2f} | {current_price - 5:.2f}\n"
            f"🛑 *الوقف:* {current_price + 3:.2f}\n"
            f"---------------------------"
        )

        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
        return "Signal Sent Successfully!", 200

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
