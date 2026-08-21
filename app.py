import os
import requests

TELEGRAM_TOKEN = "8871528209:AAEg5xRXZDahlu4VwMVmkM1b7qChGYbbJe0"
CHAT_ID = "5760283457"

def send_signal():
    try:
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        if response.status_code != 200:
            return
            
        data = response.json()
        current_price = float(data.get('price', 2500.00))
        
        # حسابات مبسطة للإشارة
        signal = "بيع / شراء ذكي"
        tp1 = current_price + 3.00
        tp2 = current_price + 6.50
        tp3 = current_price + 10.00
        sl = current_price - 4.00
        rsi = 50.0

        message = (
            f"🧞‍♂️ *الجن ابن العفاريت VIP (GitHub Action)* 🧞‍♂️\n"
            f"---------------------------\n"
            f"💎 السعر الفوري الحي: `{current_price:.2f}`\n"
            f"💎 نقطة الدخول المقترحة: `{current_price:.2f}`\n\n"
            f"🎯 *الأهداف الاستراتيجية الذكية (TP):*\n"
            f"• *TP1:* `{tp1:.2f}`\n"
            f"• *TP2:* `{tp2:.2f}`\n"
            f"• *TP3:* `{tp3:.2f}`\n\n"
            f"🛑 *حماية الخسارة الآمنة (SL):* `{sl:.2f}`\n"
            f"---------------------------\n"
            f"⚙️ *محرك GitHub Actions المباشر*\n"
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

if __name__ == "__main__":
    send_signal()
