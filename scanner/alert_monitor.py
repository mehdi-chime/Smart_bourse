
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
    from scanner.alert_config import (
        EITAA_TOKEN, EITAA_CHAT_ID, WATCH_SYMBOLS,
        CHECK_INTERVAL, STRONG_BUY_RATIO, STRONG_SELL_RATIO,
        ALERT_ON_QUEUE, ALERT_ON_STRONG, ALERT_ON_BIG_CHANGE,
        BIG_CHANGE_PCT, MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR,
        MARKET_CLOSE_MINUTE,
    )
except Exception as e:
    print("Config error:", e)
    sys.exit(1)


ALERTED_FILE = PROJECT_ROOT / "data" / "alerts_sent.json"


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


def load_alerted():
    if ALERTED_FILE.exists():
        try:
            with open(ALERTED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            today = datetime.now().strftime("%Y-%m-%d")
            if data.get("date") == today:
                return data.get("sent", {})
        except Exception:
            pass
    return {}


def save_alerted(sent):
    ALERTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERTED_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sent": sent,
        }, f, ensure_ascii=False, indent=2)


def send_eitaa(text):
    url = "https://eitaayar.ir/api/" + EITAA_TOKEN + "/sendMessage"
    try:
        r = requests.get(url, params={
            "chat_id": EITAA_CHAT_ID,
            "text": text,
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("   send error:", str(e)[:80])
        return False


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


def is_market_time():
    now = datetime.now()
    h = now.hour
    m = now.minute
    # ایران: Sat-Wed
    wd = now.weekday()
    if wd not in [5, 6, 0, 1, 2]:
        return False
    if h < MARKET_OPEN_HOUR:
        return False
    if h > MARKET_CLOSE_HOUR:
        return False
    if h == MARKET_CLOSE_HOUR and m > MARKET_CLOSE_MINUTE:
        return False
    return True


def check_and_alert():
    df = att.get_live_market()
    if df is None or df.empty:
        return

    sent = load_alerted()
    today = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%H:%M:%S")

    for item in WATCH_SYMBOLS:
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

        # ذخیره آخرین وضعیت
        key_prev = symbol + "_prev"

        # بررسی صف خرید
        if ALERT_ON_QUEUE and buy_q > 0 and sell_q == 0:
            key = symbol + "_BUY_QUEUE"
            if key not in sent:
                msg = "🟢 صف خرید: " + symbol + "\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                msg += "صف خرید: " + "{:,}".format(int(buy_q)) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    sent[key] = now_str
                    print("   [+] " + symbol + " BUY QUEUE")

        # صف فروش
        if ALERT_ON_QUEUE and sell_q > 0 and buy_q == 0:
            key = symbol + "_SELL_QUEUE"
            if key not in sent:
                msg = "🔴 صف فروش: " + symbol + "\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                msg += "صف فروش: " + "{:,}".format(int(sell_q)) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    sent[key] = now_str
                    print("   [-] " + symbol + " SELL QUEUE")

        # نسبت قوی
        if ALERT_ON_STRONG and ratio > STRONG_BUY_RATIO and ratio < 1000:
            key = symbol + "_STRONG_BUY"
            if key not in sent:
                msg = "⭐ خرید قوی: " + symbol + "\n"
                msg += "نسبت خرید/فروش: " + "{:.2f}".format(ratio) + "\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    sent[key] = now_str
                    print("   [⭐] " + symbol + " STRONG BUY")

        if ALERT_ON_STRONG and ratio > 0 and ratio < STRONG_SELL_RATIO:
            key = symbol + "_STRONG_SELL"
            if key not in sent:
                msg = "⚠️ فروش قوی: " + symbol + "\n"
                msg += "نسبت خرید/فروش: " + "{:.2f}".format(ratio) + "\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    sent[key] = now_str
                    print("   [⚠️] " + symbol + " STRONG SELL")

        # تغییر بزرگ
        if ALERT_ON_BIG_CHANGE and abs(change) > BIG_CHANGE_PCT:
            key = symbol + "_BIG_CHANGE_" + ("up" if change > 0 else "down")
            if key not in sent:
                emoji = "🚀" if change > 0 else "📉"
                msg = emoji + " تغییر بزرگ: " + symbol + "\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + "\n"
                msg += "تغییر: " + "{:+.2f}%".format(change) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    sent[key] = now_str
                    print("   [" + emoji + "] " + symbol + " BIG CHANGE")

    save_alerted(sent)


def main():
    print()
    print("=" * 75)
    print("  Smart_Bourse Alert Monitor - Eitaa")
    print("=" * 75)
    print()
    print("  Token: " + (EITAA_TOKEN[:8] + "..." if EITAA_TOKEN != "PUT_YOUR_TOKEN_HERE" else "NOT SET!"))
    print("  Chat ID: " + EITAA_CHAT_ID)
    print("  Watch: " + str(len(WATCH_SYMBOLS)) + " symbols")
    print("  Interval: " + str(CHECK_INTERVAL) + "s")
    print("  Market: " + str(MARKET_OPEN_HOUR) + ":00 - " + str(MARKET_CLOSE_HOUR) + ":" + str(MARKET_CLOSE_MINUTE).zfill(2))
    print()

    if EITAA_TOKEN == "PUT_YOUR_TOKEN_HERE":
        print("  [ERROR] Set your EITAA_TOKEN in scanner/alert_config.py")
        return

    print("  Press Ctrl+C to stop")
    print()

    count = 0
    while True:
        try:
            now_str = datetime.now().strftime("%H:%M:%S")
            if is_market_time():
                check_and_alert()
                count += 1
                if count % 20 == 0:
                    print("   [" + now_str + "] checked " + str(count) + " times")
            else:
                if count % 60 == 0:
                    print("   [" + now_str + "] market closed - waiting")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print()
            print("  Stopped. Total checks: " + str(count))
            break
        except Exception as e:
            print("   error: " + str(e)[:100])
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
