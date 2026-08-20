import os
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from flask import Flask
from telegram import Bot
import asyncio

app = Flask(__name__)

# بيانات التوكن والـ Chat ID المحدثة
TELEGRAM_TOKEN = "8871528209:AAElReV2Tv2j2xTpmYR6IGDeo5UTQqTsB1k"
CHAT_ID = "5760283457"

async def send_signal():
    try:
        # 1. سحب بيانات الذهب الحقيقية (آخر 5 أيام بفاصل ساعة)
        gold = yf.Ticker("GC=F") 
        data = gold.history(period="5d", interval="1h")
        
        if data.empty:
            return "No data found"

        # 2. حساب مؤشر RSI الحقيقي باستخدام pandas_ta
        rsi = ta.rsi(data['Close'], length=14)
        current_rsi = rsi.iloc[-1]
        current_price = data['Close'].iloc[-1]

        # 3. لوجيك الإشارة (احترافي ودقيق)
        signal_type = "شراء BUY 🟢" if current_rsi < 30 else ("بيع SELL 🔴" if current_rsi > 70 else "انتظار (No Signal)")
        
        if signal_type == "انتظار (No Signal)":
            return "Market in neutral zone, no signal sent."

        # 4. تنسيق الرسالة الاحترافية
        message = (
            f"🔥 *Mody Luck Gold System (Live)* 🔥\n"
            f"---------------------------\n"
            f"💎 السعر الفوري: {current_price:.2f}\n"
            f"💎 نوع الإشارة: {signal_type}\n"
            f"📊 مؤشر RSI الحقيقي: {current_rsi:.2f}\n"
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
    # تشغيل المهمة غير المتزامنة
    result = asyncio.run(send_signal())
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
