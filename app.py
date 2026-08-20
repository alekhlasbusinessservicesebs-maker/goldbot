import os
import yfinance as yf
import pandas as pd
from flask import Flask
from telegram import Bot
import asyncio

app = Flask(__name__)

# التوكن والـ ID
TELEGRAM_TOKEN = "8871528209:AAElReV2Tv2j2xTpmYR6IGDeo5UTQqTsB1k"
CHAT_ID = "5760283457"

async def send_signal():
    try:
        # استخدام yfinance لسحب البيانات
        ticker = yf.Ticker("GC=F")
        hist = ticker.history(period="1mo", interval="1h")
        
        if hist.empty:
            return "No data"

        # حساب RSI بطريقة مبسطة جداً
        close = hist['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        price = close.iloc[-1]

        # إرسال الإشارة
        if current_rsi < 30 or current_rsi > 70:
            signal = "شراء" if current_rsi < 30 else "بيع"
            bot = Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(chat_id=CHAT_ID, text=f"إشارة {signal} - سعر: {price:.2f} - RSI: {current_rsi:.2f}")
            return "Sent"
        
        return "No signal"
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return asyncio.run(send_signal())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
