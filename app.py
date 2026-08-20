import os
import time
import requests
from flask import Flask

app = Flask(__name__)

# إعدادات بوت تليجرام (تأكد إن التوكن والتشات آي دي متظبطين في الـ Environment Variables على Render)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7942761622:AAGjGv6-v8zJ3Z2Qx... (التوكن بتاعك)")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1314358688")

# قائمة لتخزين آخر الأسعار عشان نحسب اتجاه السوق البسيط (SMA)
price_history = []

def get_gold_price():
    """سحب السعر الفوري للذهب من الـ API المجاني"""
    try:
        url = "https://www.gold-api.com/api/XAU/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        price = float(data.get("price") or data.get("ask") or 0)
        return price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def analyze_market(current_price):
    """تحليل حركة السعر بذكاء خفيف بناءً على متوسط الأسعار السابقة"""
    global price_history
    
    # إضافة السعر الحالي للقائمة (نحتفظ بأخر 4 أسعار يعني ساعة تقريباً)
    price_history.append(current_price)
    if len(price_history) > 4:
        price_history.pop(0)
        
    # لو لسه مجمعناش بيانات كفاية، ندي تحليل محايد مبدئي
    if len(price_history) < 2:
        return "NEUTRAL", current_price * 0.998, current_price * 1.003, current_price * 1.006
        
    # حساب المتوسط البسيط (SMA)
    sma = sum(price_history) / len(price_history)
    
    # تحديد الاتجاه بناءً على مقارنة السعر الحالي بالمتوسط
    if current_price > sma:
        trend = "STRONG BUY (صاعد بذكاء)"
        sl = current_price - 4.5  # وقف خسارة محسوب
        tp1 = current_price + 4.0
        tp2 = current_price + 8.0
        tp3 = current_price + 12.0
    else:
        trend = "STRONG SELL (هابط بذكاء)"
        sl = current_price + 4.5
        tp1 = current_price - 4.0
        tp2 = current_price - 8.0
        tp3 = current_price - 12.0
        
    return trend, sl, tp1, tp2, tp3

def send_telegram_message(message):
    """إرسال الإشارة لتليجرام"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending telegram message: {e}")

@app.route("/")
def home():
    price = get_gold_price()
    if price:
        trend, sl, tp1, tp2, tp3 = analyze_market(price)
        return f"XAUUSD Beast Bot (Smart Free) is Running! Current Price: {price} | Trend: {trend}"
    return "XAUUSD Bot is Running, waiting for price data..."

def background_bot_loop():
    """حلقة عمل البوت كل 15 دقيقة في الخلفية"""
    import threading
    def run():
        while True:
            try:
                price = get_gold_price()
                if price:
                    trend, sl, tp1, tp2, tp3 = analyze_market(price)
                    
                    message = (
                        f"🚨 *XAUUSD SMART SIGNAL (Free Pro)* 🚨\n\n"
                        f"🟡 *السعر الحالي:* `{price:.2f}`\n"
                        f"📊 *الاتجاه المحسوب:* `{trend}`\n\n"
                        f"🎯 *الأهداف المقترحة:* \n"
                        f"🔹 TP1: `{tp1:.2f}`\n"
                        f"🔹 TP2: `{tp2:.2f}`\n"
                        f"🔹 TP3: `{tp3:.2f}`\n\n"
                        f"🛑 *وقف الخسارة (SL):* `{sl:.2f}`\n"
                        f"⏱ *الفريم:* `15 Minutes (Smart Logic)`"
                    )
                    send_telegram_message(message)
            except Exception as e:
                print(f"Loop error: {e}")
            
            # الانتظار لمدة 15 دقيقة (900 ثانية)
            time.sleep(900)
            
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

# تشغيل خيط الخلفية عند بدء سيرفر الفلاسك
background_bot_loop()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
