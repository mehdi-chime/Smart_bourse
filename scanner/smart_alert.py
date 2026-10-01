
import sys
import time
import json
from datetime import datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

try:
    from scanner.alert_config import EITAA_TOKEN, EITAA_CHAT_ID
except Exception:
    EITAA_TOKEN = ""
    EITAA_CHAT_ID = ""

try:
    from scanner.smart_indicators import (
        analyze_symbol, fibonacci_levels,
        find_support_resistance, atr, bollinger
    )
    HAS_INDICATORS = True
except Exception as e:
    HAS_INDICATORS = False
    print("Indicator import warning:", e)


HOLDINGS = [
    {"name": "تابان",   "aliases": ["تابان"],                "qty": 3697,   "buy_price": None},
    {"name": "پکویر",   "aliases": ["پكوير", "پکویر"],      "qty": 23518,  "buy_price": None},
    {"name": "سمهریز",  "aliases": ["سهرمز", "سمهریز"],     "qty": 5350,   "buy_price": None},
    {"name": "احیا",    "aliases": ["احیا", "احياء"],        "qty": 49122,  "buy_price": None},
    {"name": "پیزد",    "aliases": ["پیزد"],                  "qty": 23220,  "buy_price": None},
    {"name": "خپارس",   "aliases": ["خپارس"],                 "qty": 217948, "buy_price": None},
    {"name": "خگستر",   "aliases": ["خگستر"],                 "qty": 468777, "buy_price": 4327},
    {"name": "فولاد",   "aliases": ["فولاد"],                 "qty": 431948, "buy_price": 3394},
]

CHECK_INTERVAL = 30
HISTORY_FILE = PROJECT_ROOT / "data" / "smart_alert_history.json"
SENT_FILE = PROJECT_ROOT / "data" / "smart_alert_sent.json"
INDICATOR_CACHE_FILE = PROJECT_ROOT / "data" / "indicator_cache.json"


def normalize(s):
    if not s:
        return s
    return (str(s)
            .replace("\u0643", "\u06a9")
            .replace("\u064a", "\u06cc")
            .replace("\u0649", "\u06cc")
            .replace("\u0629", "\u0647")
            .replace("\u0640", "")
            .strip())


def find_symbol(df, aliases):
    for alias in aliases:
        target = normalize(alias)
        for _, row in df.iterrows():
            if normalize(row.get("Symbol", "")) == target:
                return row
    for alias in aliases:
        target = normalize(alias)
        for _, row in df.iterrows():
            if normalize(row.get("Symbol", "")).startswith(target):
                return row
    return None


def load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_eitaa(text):
    if not EITAA_TOKEN:
        return False
    url = "https://eitaayar.ir/api/" + EITAA_TOKEN + "/sendMessage"
    try:
        r = requests.get(url, params={
            "chat_id": EITAA_CHAT_ID,
            "text": text,
        }, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def is_market_time():
    now = datetime.now()
    h, m = now.hour, now.minute
    wd = now.weekday()
    if wd not in [5, 6, 0, 1, 2]:
        return False
    if h < 9:
        return False
    if h > 12:
        return False
    if h == 12 and m > 30:
        return False
    return True


def get_indicator_cache():
    """هر ۵ دقیقه اندیکاتورها رو دوباره حساب کن"""
    cache = load_json(INDICATOR_CACHE_FILE, {})
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    if cache.get("date") != today:
        cache = {"date": today, "time": "", "data": {}}

    # اگه آخرین بار > ۵ دقیقه پیش
    last_time = cache.get("time", "")
    if last_time:
        try:
            last_dt = datetime.strptime(last_time, "%H:%M:%S")
            diff = (now - last_dt.replace(year=now.year, month=now.month, day=now.day)).total_seconds()
            if diff < 300:
                return cache.get("data", {})
        except Exception:
            pass

    # محاسبه مجدد
    result = {}
    for h in HOLDINGS:
        symbol = h["name"]
        try:
            data = analyze_symbol(symbol)
            if data:
                result[symbol] = data
        except Exception:
            pass

    cache["data"] = result
    cache["time"] = now.strftime("%H:%M:%S")
    save_json(INDICATOR_CACHE_FILE, cache)
    return result


def analyze_and_alert():
    df = att.get_live_market()
    if df is None or df.empty:
        return

    history = load_json(HISTORY_FILE, {})
    sent = load_json(SENT_FILE, {})
    today = datetime.now().strftime("%Y-%m-%d")
    if sent.get("date") != today:
        sent = {"date": today, "signals": {}}
    sent_signals = sent.get("signals", {})

    # اندیکاتورها
    indicators = get_indicator_cache() if HAS_INDICATORS else {}

    now_str = datetime.now().strftime("%H:%M:%S")
    now_ts = datetime.now().isoformat()

    for item in HOLDINGS:
        name = item["name"]
        aliases = item["aliases"]

        r = find_symbol(df, aliases)
        if r is None:
            continue

        symbol = str(r.get("Symbol", name))
        price = float(r.get("Last") or r.get("Close") or 0)
        change = float(r.get("ChangePct") or 0)
        buy_q = float(r.get("BuyQueueVolume") or 0)
        sell_q = float(r.get("SellQueueVolume") or 0)
        vol_buy = float(r.get("Vol_buy_retail") or 0)
        vol_sell = float(r.get("Vol_sell_retail") or 0)

        if vol_sell > 0:
            ratio = vol_buy / vol_sell
        elif vol_buy > 0:
            ratio = 9999
        else:
            ratio = 0

        if symbol not in history:
            history[symbol] = []
        history[symbol].append({
            "time": now_str,
            "price": price,
            "change_pct": change,
            "buy_queue": buy_q,
            "sell_queue": sell_q,
            "ratio": ratio,
        })
        history[symbol] = history[symbol][-50:]

        prev = history[symbol][-2] if len(history[symbol]) >= 2 else None

        ind = indicators.get(name, {})

        # ═══ 1. صف خرید ریخت ═══
        if prev:
            prev_bq = prev.get("buy_queue", 0)
            prev_sq = prev.get("sell_queue", 0)

            if prev_bq > 0 and buy_q == 0:
                key = symbol + "_QUEUE_DROPPED_" + today
                if key not in sent_signals:
                    msg = "🚨 " + symbol + " — صف خرید ریخت!\n"
                    msg += "━━━━━━━━━━━━━━━━━━\n"
                    msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                    msg += "صف قبل: " + "{:,}".format(int(prev_bq)) + "\n"
                    # اضافه کن حمایت Fibonacci
                    if ind and ind.get("fib_support"):
                        fs = ind["fib_support"]
                        msg += "Fib " + fs[0] + "%: " + "{:,}".format(int(fs[1])) + "\n"
                    if ind and ind.get("nearest_support"):
                        msg += "حمایت: " + "{:,}".format(int(ind["nearest_support"])) + "\n"
                    if ind and ind.get("stop_loss_atr"):
                        msg += "🛑 حد ضرر ATR: " + "{:,}".format(int(ind["stop_loss_atr"])) + "\n"
                    msg += "⏰ " + now_str
                    if send_eitaa(msg):
                        sent_signals[key] = now_str
                        print("   [🚨] " + symbol + " QUEUE DROPPED")

            if prev_sq > 0 and sell_q == 0:
                key = symbol + "_SELL_DROPPED_" + today
                if key not in sent_signals:
                    msg = "✅ " + symbol + " — صف فروش ریخت!\n"
                    msg += "━━━━━━━━━━━━━━━━━━\n"
                    msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                    msg += "صف قبل: " + "{:,}".format(int(prev_sq)) + "\n"
                    if ind and ind.get("fib_support"):
                        fs = ind["fib_support"]
                        msg += "Fib " + fs[0] + "%: " + "{:,}".format(int(fs[1])) + "\n"
                    if ind and ind.get("bollinger"):
                        bb = ind["bollinger"]
                        if price < bb["lower"]:
                            msg += "🟢 زیر Bollinger\n"
                    msg += "⏰ " + now_str
                    if send_eitaa(msg):
                        sent_signals[key] = now_str
                        print("   [✅] " + symbol + " SELL DROPPED")

        # ═══ 2. صف خرید جدید ═══
        if buy_q > 0 and sell_q == 0:
            key = symbol + "_BUY_QUEUE_NEW_" + today
            if key not in sent_signals:
                msg = "🟢 " + symbol + " — صف خرید!\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                msg += "صف: " + "{:,}".format(int(buy_q)) + "\n"
                if ind and ind.get("fib_resistance"):
                    fr = ind["fib_resistance"]
                    msg += "مقاومت Fib: " + "{:,}".format(int(fr[1])) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    sent_signals[key] = now_str
                    print("   [🟢] " + symbol + " BUY QUEUE")

        # ═══ 3. صف فروش جدید ═══
        if sell_q > 0 and buy_q == 0:
            key = symbol + "_SELL_QUEUE_NEW_" + today
            if key not in sent_signals:
                msg = "🔴 " + symbol + " — صف فروش!\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                msg += "صف: " + "{:,}".format(int(sell_q)) + "\n"
                if ind and ind.get("fib_support"):
                    fs = ind["fib_support"]
                    msg += "حمایت Fib: " + "{:,}".format(int(fs[1])) + "\n"
                if ind and ind.get("nearest_support"):
                    msg += "حمایت: " + "{:,}".format(int(ind["nearest_support"])) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    sent_signals[key] = now_str
                    print("   [🔴] " + symbol + " SELL QUEUE")

        # ═══ 4. زیر Bollinger (فرصت خرید) ═══
        if ind and ind.get("bollinger"):
            bb = ind["bollinger"]
            if price < bb["lower"]:
                key = symbol + "_BOLLINGER_LOW_" + today
                if key not in sent_signals:
                    msg = "🟢 " + symbol + " — زیر Bollinger\n"
                    msg += "━━━━━━━━━━━━━━━━━━\n"
                    msg += "قیمت: " + "{:,}".format(int(price)) + "\n"
                    msg += "کف BB: " + "{:,}".format(int(bb["lower"])) + "\n"
                    msg += "میانه: " + "{:,}".format(int(bb["middle"])) + "\n"
                    msg += "🟢 فرصت خرید\n"
                    msg += "⏰ " + now_str
                    if send_eitaa(msg):
                        sent_signals[key] = now_str
                        print("   [🟢] " + symbol + " BB LOW")

            if price > bb["upper"]:
                key = symbol + "_BOLLINGER_HIGH_" + today
                if key not in sent_signals:
                    msg = "🔴 " + symbol + " — بالای Bollinger\n"
                    msg += "قیمت: " + "{:,}".format(int(price)) + "\n"
                    msg += "سقف BB: " + "{:,}".format(int(bb["upper"])) + "\n"
                    msg += "🔴 احتمال اصلاح\n"
                    msg += "⏰ " + now_str
                    if send_eitaa(msg):
                        sent_signals[key] = now_str
                        print("   [🔴] " + symbol + " BB HIGH")

        # ═══ 5. نزدیک حمایت قوی Fibonacci ═══
        if ind and ind.get("fib_support") and ind.get("fib_support")[0] in ["61.8", "50.0"]:
            fs = ind["fib_support"]
            dist_pct = abs(price - fs[1]) / fs[1] * 100
            if dist_pct < 1.5:
                key = symbol + "_FIB_" + fs[0] + "_" + today
                if key not in sent_signals:
                    msg = "🟢 " + symbol + " — نزدیک حمایت Fib\n"
                    msg += "━━━━━━━━━━━━━━━━━━\n"
                    msg += "قیمت: " + "{:,}".format(int(price)) + "\n"
                    msg += "Fib " + fs[0] + "%: " + "{:,}".format(int(fs[1])) + "\n"
                    msg += "🟢 سطح قوی — فرصت خرید\n"
                    msg += "⏰ " + now_str
                    if send_eitaa(msg):
                        sent_signals[key] = now_str
                        print("   [🟢] " + symbol + " FIB SUPPORT")

        # ═══ 6. خگستر/فولاد سود/ضرر ═══
        buy_p = item.get("buy_price")
        if buy_p:
            profit_pct = (price - buy_p) / buy_p * 100

            if profit_pct > 5:
                key = symbol + "_PROFIT_5_" + today
                if key not in sent_signals:
                    msg = "💰 " + symbol + " — سود بالای ۵٪\n"
                    msg += "خرید: " + "{:,}".format(int(buy_p)) + "\n"
                    msg += "الآن: " + "{:,}".format(int(price)) + "\n"
                    msg += "سود: " + "{:+.2f}%".format(profit_pct) + "\n"
                    msg += "⏰ " + now_str
                    if send_eitaa(msg):
                        sent_signals[key] = now_str
                        print("   [💰] " + symbol + " PROFIT")

            if profit_pct < -5:
                key = symbol + "_LOSS_5_" + today
                if key not in sent_signals:
                    msg = "⚠️ " + symbol + " — ضرر بالای ۵٪\n"
                    msg += "خرید: " + "{:,}".format(int(buy_p)) + "\n"
                    msg += "الآن: " + "{:,}".format(int(price)) + "\n"
                    msg += "ضرر: " + "{:+.2f}%".format(profit_pct) + "\n"
                    if ind and ind.get("stop_loss_atr"):
                        msg += "🛑 حد ضرر ATR: " + "{:,}".format(int(ind["stop_loss_atr"])) + "\n"
                    msg += "⏰ " + now_str
                    if send_eitaa(msg):
                        sent_signals[key] = now_str
                        print("   [⚠️] " + symbol + " LOSS")

    save_json(HISTORY_FILE, history)
    sent["signals"] = sent_signals
    save_json(SENT_FILE, sent)


def main():
    print()
    print("=" * 75)
    print("  Smart_Bourse — Smart Alert v3")
    print("=" * 75)
    print()
    print("  Token: " + (EITAA_TOKEN[:10] + "..." if EITAA_TOKEN else "NOT SET"))
    print("  Chat ID: " + EITAA_CHAT_ID)
    print("  Indicators: " + ("ENABLED" if HAS_INDICATORS else "DISABLED"))
    print("  Holdings: " + str(len(HOLDINGS)) + " symbols")
    print()
    print("  Alerts:")
    print("     🚨 صف خرید ریخت")
    print("     ✅ صف فروش ریخت")
    print("     🟢 صف خرید جدید")
    print("     🔴 صف فروش جدید")
    print("     🟢/🔴 Bollinger")
    print("     🟢 حمایت Fibonacci")
    print("     💰 سود > ۵٪")
    print("     ⚠️ ضرر > ۵٪")
    print()
    print("  Press Ctrl+C to stop")
    print()

    count = 0
    while True:
        try:
            now_str = datetime.now().strftime("%H:%M:%S")
            if is_market_time():
                analyze_and_alert()
                count += 1
                if count % 40 == 0:
                    print("   [" + now_str + "] checked " + str(count))
            else:
                if count == 0:
                    print("   [" + now_str + "] waiting...")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("  Stopped. Total: " + str(count))
            break
        except Exception as e:
            print("   error: " + str(e)[:100])
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
