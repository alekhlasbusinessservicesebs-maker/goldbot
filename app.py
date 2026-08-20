import os
import yfinance as yf
from flask import Flask
from telegram import Bot
import asyncio

app = Flask(__name__)

TELEGRAM_TOKEN = "8871528209:AAElReV2Tv2j2xTpmYR6IGDeo5UTQqTsB1k"
CHAT_ID = "5760283457"

async def send_signal():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="2d", interval="1h")
        
        if data.empty:
            return "No data found"

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

        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        return "Signal Sent Successfully"

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return asyncio.run(send_signal())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
