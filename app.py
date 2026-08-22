import os
import time
import threading
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from flask import Flask

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
SYMBOL = os.getenv("GOLD_SYMBOL", "XAU/USD")
TIMEFRAME = os.getenv("TIMEFRAME", "15min")
TIMEZONE_NAME = os.getenv("TIMEZONE", "Asia/Dubai")
MIN_SCORE_TO_SIGNAL = float(os.getenv("MIN_SCORE", "75"))

TZ = pytz.timezone(TIMEZONE_NAME)

last_candle_time = None
last_signal_type = None


def get_market_data():
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={SYMBOL}&interval={TIMEFRAME}&outputsize=150&apikey={TWELVE_DATA_API_KEY}"
    )
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if "values" not in data:
            print(f"API Error or no data: {data}")
            return None
        df = pd.DataFrame(data["values"])
        df = df.iloc[::-1].reset_index(drop=True)
        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)
        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
        else:
            df["volume"] = 0.0
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None
def calculate_all_indicators(df):
    
    close = df["close"]
    
    high = df["high"]
    
    low = df["low"]
    
    open_p = df["open"]
    
    volume = df["volume"]

    df["EMA_9"] = close.ewm(span=9, adjust=False).mean()
    df["EMA_20"] = close.ewm(span=20, adjust=False).mean()
    df["EMA_50"] = close.ewm(span=50, adjust=False).mean()
    df["EMA_200"] = close.ewm(span=200, adjust=False).mean()
    df["SMA_20"] = close.rolling(window=20).mean()
    df["SMA_50"] = close.rolling(window=50).mean()

    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))

    rsi_min = df["RSI"].rolling(window=14).min()
    rsi_max = df["RSI"].rolling(window=14).max()
    df["Stoch_RSI"] = (df["RSI"] - rsi_min) / (rsi_max - rsi_min + 1e-10) * 100

    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    rolling_mean = close.rolling(window=20).mean()
    rolling_std = close.rolling(window=20).std()
    df["BB_Mid"] = rolling_mean
    df["BB_Upper"] = rolling_mean + (rolling_std * 2)
    df["BB_Lower"] = rolling_mean - (rolling_std * 2)
    df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / (rolling_mean + 1e-10)

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(window=14).mean()

    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    df["Stoch_K"] = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    df["Stoch_D"] = df["Stoch_K"].rolling(window=3).mean()

    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)
    tr_smooth = tr.rolling(window=14).mean()
    plus_di = 100 * (plus_dm.rolling(window=14).mean() / (tr_smooth + 1e-10))
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / (tr_smooth + 1e-10))
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10)
    df["ADX"] = dx.rolling(window=14).mean()
    df["Plus_DI"] = plus_di
    df["Minus_DI"] = minus_di

    tp = (high + low + close) / 3
    tp_sma = tp.rolling(window=20).mean()
    tp_md = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=False)
    df["CCI"] = (tp - tp_sma) / (0.015 * (tp_md + 1e-10))

    df["PSAR"] = close.copy()
    af = 0.02
    max_af = 0.2
    trend = 1
    ep = high.iloc[0]
    sar = low.iloc[0]
    psar_list = [sar]
    for i in range(1, len(df)):
        prev_sar = psar_list[-1]
        sar = prev_sar + af * (ep - prev_sar)
        if trend == 1:
            if low.iloc[i] < sar:
                trend = -1
                sar = ep
                ep = low.iloc[i]
                af = 0.02
            else:
                if high.iloc[i] > ep:
                    ep = high.iloc[i]
                    af = min(af + 0.02, max_af)
        else:
            if high.iloc[i] > sar:
                trend = 1
                sar = ep
                ep = high.iloc[i]
                af = 0.02
            else:
                if low.iloc[i] < ep:
                    ep = low.iloc[i]
                    af = min(af + 0.02, max_af)
        psar_list.append(sar)
    df["PSAR"] = psar_list

    hl2 = (high + low) / 2
    df["Supertrend_Upper"] = hl2 + (3 * df["ATR"])
    df["Supertrend_Lower"] = hl2 - (3 * df["ATR"])

    highest_20 = high.rolling(window=20).max()
    lowest_20 = low.rolling(window=20).min()
    df["Donchian_Upper"] = highest_20
    df["Donchian_Lower"] = lowest_20

    kc_mid = close.ewm(span=20, adjust=False).mean()
    df["Keltner_Upper"] = kc_mid + (2 * df["ATR"])
    df["Keltner_Lower"] = kc_mid - (2 * df["ATR"])

    df["Williams_R"] = -100 * (highest_high - close) / (highest_high - lowest_low + 1e-10)

    df["ROC"] = close.pct_change(periods=12) * 100

    aroon_up = high.rolling(window=25).apply(lambda x: float(np.argmax(x)) / 24 * 100, raw=True)
    aroon_down = low.rolling(window=25).apply(lambda x: float(np.argmin(x)) / 24 * 100, raw=True)
    df["Aroon_Up"] = aroon_up
    df["Aroon_Down"] = aroon_down

    df["BOP"] = (close - open_p) / (high - low + 1e-10)

    df["DPO"] = close.shift(11) - close.rolling(window=20).mean()

    ema1 = close.ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df["TRIX"] = ema3.pct_change() * 100

    return df
def score_signal(df):
    
    last = df.iloc[-2]  # آخر شمعة مكتملة، وليس الشمعة الحالية
    
    scores = {"BUY": 0.0,"SELL": 0.0,}
   
    reasons = []

    def vote(name, direction, weight=1.0):
        if direction in scores:
            scores[direction] += weight
            reasons.append((name, direction, weight))

    close = float(last["close"])

    # EMA وSMA
    if last["EMA_20"] > last["EMA_50"] > last["EMA_200"]:
        vote("EMA Trend", "BUY", 2.0)
    elif last["EMA_20"] < last["EMA_50"] < last["EMA_200"]:
        vote("EMA Trend", "SELL", 2.0)

    if last["SMA_20"] > last["SMA_50"]:
        vote("SMA Trend", "BUY", 1.0)
    elif last["SMA_20"] < last["SMA_50"]:
        vote("SMA Trend", "SELL", 1.0)

    # MACD
    if last["MACD"] > last["MACD_Signal"] and last["MACD_Hist"] > 0:
        vote("MACD", "BUY", 1.5)
    elif last["MACD"] < last["MACD_Signal"] and last["MACD_Hist"] < 0:
        vote("MACD", "SELL", 1.5)

    # RSI
    if 52 <= last["RSI"] <= 70:
        vote("RSI", "BUY", 1.0)
    elif 30 <= last["RSI"] <= 48:
        vote("RSI", "SELL", 1.0)

    # Stochastic
    if last["Stoch_K"] > last["Stoch_D"] and last["Stoch_K"] < 85:
        vote("Stochastic", "BUY", 1.0)
    elif last["Stoch_K"] < last["Stoch_D"] and last["Stoch_K"] > 15:
        vote("Stochastic", "SELL", 1.0)

    # ADX + DI
    if last["ADX"] >= 20:
        if last["Plus_DI"] > last["Minus_DI"]:
            vote("ADX/DI", "BUY", 1.5)
        elif last["Minus_DI"] > last["Plus_DI"]:
            vote("ADX/DI", "SELL", 1.5)

    # CCI
    if last["CCI"] > 50:
        vote("CCI", "BUY", 1.0)
    elif last["CCI"] < -50:
        vote("CCI", "SELL", 1.0)

    # Parabolic SAR
    if last["PSAR"] < close:
        vote("Parabolic SAR", "BUY", 1.0)
    elif last["PSAR"] > close:
        vote("Parabolic SAR", "SELL", 1.0)

    # Supertrend
    if close > last["Supertrend_Upper"]:
        vote("Supertrend", "BUY", 1.0)
    elif close < last["Supertrend_Lower"]:
        vote("Supertrend", "SELL", 1.0)

    # Donchian
    if close > last["Donchian_Upper"]:
        vote("Donchian Breakout", "BUY", 1.0)
    elif close < last["Donchian_Lower"]:
        vote("Donchian Breakout", "SELL", 1.0)

    # Keltner
    if close > last["Keltner_Upper"]:
        vote("Keltner Channels", "BUY", 1.0)
    elif close < last["Keltner_Lower"]:
        vote("Keltner Channels", "SELL", 1.0)

    # Williams %R
    if last["Williams_R"] > -50:
        vote("Williams %R", "BUY", 0.75)
    elif last["Williams_R"] < -50:
        vote("Williams %R", "SELL", 0.75)

    # ROC
    if last["ROC"] > 0:
        vote("ROC", "BUY", 0.75)
    elif last["ROC"] < 0:
        vote("ROC", "SELL", 0.75)

    # Aroon
    if last["Aroon_Up"] > last["Aroon_Down"]:
        vote("Aroon", "BUY", 0.75)
    elif last["Aroon_Down"] > last["Aroon_Up"]:
        vote("Aroon", "SELL", 0.75)

    # BOP
    if last["BOP"] > 0:
        vote("BOP", "BUY", 0.5)
    elif last["BOP"] < 0:
        vote("BOP", "SELL", 0.5)

    # DPO
    if last["DPO"] > 0:
        vote("DPO", "BUY", 0.5)
    elif last["DPO"] < 0:
        vote("DPO", "SELL", 0.5)

    # TRIX
    if last["TRIX"] > 0:
        vote("TRIX", "BUY", 0.5)
    elif last["TRIX"] < 0:
        vote("TRIX", "SELL", 0.5)

    # Price Action
    candle_body = abs(float(last["close"]) - float(last["open"]))
    candle_range = float(last["high"]) - float(last["low"])

    if candle_range > 0:
        body_ratio = candle_body / candle_range

        if last["close"] > last["open"] and body_ratio >= 0.55:
            vote("Price Action", "BUY", 1.0)
        elif last["close"] < last["open"] and body_ratio >= 0.55:
            vote("Price Action", "SELL", 1.0)

    total_weight = sum(weight for _, _, weight in reasons)

    if total_weight <= 0:
        return {
            "direction": "WAIT",
            "score": 0.0,
            "reasons": [],
        }

    buy_score = scores["BUY"]
    sell_score = scores["SELL"]
    best_direction = "BUY" if buy_score > sell_score else "SELL"
    best_score = max(buy_score, sell_score)

    # نسبة اتفاق المؤشرات مع الاتجاه الأقوى
    agreement = (best_score / total_weight) * 100

    # فلتر صرامة إضافي: الاتجاه يجب أن يتفوق بوضوح
    difference = abs(buy_score - sell_score)
    strong_difference = difference / total_weight * 100

    if agreement < MIN_SCORE_TO_SIGNAL or strong_difference < 12:
        best_direction = "WAIT"

    return {
        "direction": best_direction,
        "score": round(agreement, 2),
        "buy_score": round(buy_score, 2),
        "sell_score": round(sell_score, 2),
        "reasons": reasons,
    }


def calculate_trade_levels(df, direction):
    last = df.iloc[-2]
    entry = float(last["close"])
    atr = float(last["ATR"])

    if not np.isfinite(atr) or atr <= 0:
        atr = entry * 0.01

    if direction == "BUY":
        stop_loss = entry - (atr * 1.5)
        take_profit = entry + (atr * 3)
    else:
        stop_loss = entry + (atr * 1.5)
        take_profit = entry - (atr * 3)

    return {
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
    }

# ================== إرسال الرسائل إلى Telegram ==================

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()

        if response.ok and result.get("ok"):
            print("Telegram message sent successfully.")
            return True

        print(f"Telegram error: {result}")
        return False

    except Exception as error:
        print(f"Telegram request failed: {error}")
        return False


# ================== تنسيق الوقت والسعر ==================

def format_price(value):
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_datetime(value):
    try:
        timestamp = pd.Timestamp(value)

        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        else:
            timestamp = timestamp.tz_convert("UTC")

        dubai_time = timestamp.tz_convert(TZ)
        return dubai_time.strftime("%Y-%m-%d %H:%M")

    except Exception:
        return str(value)


# ================== فلتر التذبذب والأخبار ==================

def news_volatility_filter(df):
    """
    لا يعتمد على أخبار وهمية.
    يوقف الإشارة عند وجود حركة غير طبيعية مقارنة بمتوسط ATR.
    """

    if len(df) < 40:
        return True, "بيانات غير كافية"

    current = df.iloc[-1]
    previous = df.iloc[-21:-1]

    current_range = float(current["high"] - current["low"])
    average_range = float((previous["high"] - previous["low"]).mean())
    current_atr = float(current["ATR"])
    average_atr = float(previous["ATR"].mean())

    if average_range <= 0 or average_atr <= 0:
        return False, ""

    abnormal_candle = current_range >= average_range * 2.5
    abnormal_atr = current_atr >= average_atr * 1.8

    if abnormal_candle or abnormal_atr:
        return True, "تذبذب غير طبيعي؛ احتمال خبر قوي"

    return False, ""


# ================== تحليل الإشارة ==================

def calculate_signal(df):
    if df is None or len(df) < 80:
        return {
            "type": "WAIT",
            "score": 0.0,
            "reason": "بيانات غير كافية للتحليل",
        }

    current = df.iloc[-1]
    previous = df.iloc[-2]

    buy_votes = 0.0
    sell_votes = 0.0
    total_weight = 0.0
    reasons = []

    def vote(condition_buy, condition_sell, weight, name):
        nonlocal buy_votes, sell_votes, total_weight

        total_weight += weight

        if condition_buy:
            buy_votes += weight
            reasons.append(f"{name}: شراء")
        elif condition_sell:
            sell_votes += weight
            reasons.append(f"{name}: بيع")

    close = float(current["close"])
    atr = float(current["ATR"])

    if not np.isfinite(atr) or atr <= 0:
        return {
            "type": "WAIT",
            "score": 0.0,
            "reason": "قيمة ATR غير صالحة",
        }

    # الاتجاه العام
    vote(
        current["EMA_20"] > current["EMA_50"],
        current["EMA_20"] < current["EMA_50"],
        2.0,
        "EMA20/50",
    )

    vote(
        current["EMA_50"] > current["EMA_200"],
        current["EMA_50"] < current["EMA_200"],
        2.0,
        "EMA50/200",
    )

    vote(
        current["SMA_20"] > current["SMA_50"],
        current["SMA_20"] < current["SMA_50"],
        1.0,
        "SMA20/50",
    )

    # الزخم
    vote(
        current["RSI"] > 55,
        current["RSI"] < 45,
        1.5,
        "RSI",
    )

    vote(
        current["MACD"] > current["MACD_Signal"],
        current["MACD"] < current["MACD_Signal"],
        2.0,
        "MACD",
    )

    vote(
        current["MACD_Hist"] > 0 and current["MACD_Hist"] > previous["MACD_Hist"],
        current["MACD_Hist"] < 0 and current["MACD_Hist"] < previous["MACD_Hist"],
        1.5,
        "MACD Histogram",
    )

    vote(
        current["Stoch_K"] > current["Stoch_D"] and current["Stoch_K"] > 50,
        current["Stoch_K"] < current["Stoch_D"] and current["Stoch_K"] < 50,
        1.0,
        "Stochastic",
    )

    vote(
        current["Stoch_RSI"] > 55,
        current["Stoch_RSI"] < 45,
        1.0,
        "Stochastic RSI",
    )

    vote(
        current["CCI"] > 50,
        current["CCI"] < -50,
        1.0,
        "CCI",
    )

    vote(
        current["Williams_R"] > -50,
        current["Williams_R"] < -50,
        0.75,
        "Williams %R",
    )

    vote(
        current["ROC"] > 0,
        current["ROC"] < 0,
        0.75,
        "ROC",
    )

    vote(
        current["ADX"] >= 20 and current["Plus_DI"] > current["Minus_DI"],
        current["ADX"] >= 20 and current["Minus_DI"] > current["Plus_DI"],
        1.5,
        "ADX",
    )

    vote(
        current["Aroon_Up"] > current["Aroon_Down"],
        current["Aroon_Down"] > current["Aroon_Up"],
        1.0,
        "Aroon",
    )

    vote(
        current["BOP"] > 0,
        current["BOP"] < 0,
        0.75,
        "BOP",
    )

    vote(
        current["TRIX"] > 0,
        current["TRIX"] < 0,
        0.75,
        "TRIX",
    )

    # الاتجاه والسعر
    vote(
        close > current["PSAR"],
        close < current["PSAR"],
        1.25,
        "Parabolic SAR",
    )

    vote(
        close > current["Supertrend_Lower"],
        close < current["Supertrend_Upper"],
        1.0,
        "Supertrend",
    )

    vote(
        close > current["BB_Mid"],
        close < current["BB_Mid"],
        1.0,
        "Bollinger Bands",
    )

# كمل داخل calculate_signal قبل نهاية الدالة
    vote(
        close > current["Donchian_Upper"],
        close < current["Donchian_Lower"],
        1.0,
        "Donchian",
    )

    buy_score = buy_votes
    sell_score = sell_votes
    best_score = max(buy_score, sell_score)

    if total_weight <= 0:
        signal_type = "WAIT"
        agreement = 0.0
    else:
        signal_type = "BUY" if buy_score > sell_score else "SELL"
        agreement = (best_score / total_weight) * 100

        if agreement < MIN_SCORE_TO_SIGNAL:
            signal_type = "WAIT"

    return {
        "type": signal_type,
        "score": round(agreement, 2),
        "reason": " | ".join(reasons),
    }


def process_market():
    global last_candle_time, last_signal_type

    df = get_market_data()

    if df is None:
        message = (
            "🧞‍♂️ تحليل الذهب كل 15 دقيقة\n\n"
            "⏸️ السوق مغلق أو لا توجد بيانات حاليًا.\n"
            "لا توجد إشارة تداول الآن."
        )
        sent = send_telegram_message(message)
        print(f"Market closed message sent: {sent}")
        return

    df = calculate_all_indicators(df)

    signal = calculate_signal(df)

    if signal["type"] == "WAIT":
        last = df.iloc[-2]
        message = f"""
🧞‍♂️ تحليل الذهب كل 15 دقيقة

⏸️ الاتجاه: انتظار / غير مؤكد
💎 السعر الحالي: {format_price(last["close"])}
📊 قوة الاتجاه: {signal["score"]}%

⚠️ لا توجد أفضلية واضحة للشراء أو البيع.
راقب الشارت ولا تدخل إلا بعد تأكيد الحركة.
"""
    sent = send_telegram_message(message)
    print(f"Signal sent: {sent}")
        
    message = f"""
🧞‍♂️ VIP (Live Trend) الجن ابن العفاريت 🧞‍♂️

💎 السعر الفوري الحي: {format_price(levels["entry"])}
💎 نوع الإشارة: {"شراء 🟢" if signal["type"] == "BUY" else "بيع 🔴"}
💎 نقطة الدخول: {format_price(levels["entry"])}

🎯 الهدف: {format_price(levels["take_profit"])}
🛑 وقف الخسارة: {format_price(levels["stop_loss"])}

📊 قوة الإشارة: {signal["score"]}%
⚙️ تحليل الزخم اللحظي الحقيقي
"""
    
    sent = send_telegram_message(message)
    print(f"Signal sent: {sent}")
# ================== نقاط الخدمة والتشغيل ==================

@app.get("/")
def home():
    return {
        "status": "running",
        "service": "ModyGoldBot",
        "timezone": TIMEZONE_NAME,
        "timeframe": TIMEFRAME,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/run")
def run_signal():
    try:
        process_market()
        return {"status": "processed"}
    except Exception as exc:
        print(f"Processing error: {exc}")
        return {"status": "error", "message": str(exc)}, 500


def scheduled_loop():
    """
    تشغيل اختياري كل خمس دقائق داخل الخدمة.
    يمكن تعطيله بوضع RUN_INTERNAL_LOOP=false في Render.
    """
    enabled = os.getenv("RUN_INTERNAL_LOOP", "false").lower() == "true"

    if not enabled:
        return

    while True:
        try:
            process_market()
        except Exception as exc:
            print(f"Scheduled loop error: {exc}")

        time.sleep(300)

if __name__ == "__main__":
    if os.getenv("GITHUB_ACTIONS") == "true":
        try:
            process_market()
            print("Processing completed successfully.")

        except Exception as exc:
            print(f"Processing error: {exc}")
            raise
    else:
        worker = threading.Thread(target=scheduled_loop, daemon=True)
        worker.start()

        port = int(os.getenv("PORT", "10000"))
        app.run(host="0.0.0.0", port=port)

