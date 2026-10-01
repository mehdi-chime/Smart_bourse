
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
except Exception as e:
    print("Config error:", e)
    sys.exit(1)


# ═══════════════════════════════════════════════════════════
# پرتفوی خودت - فقط اینا رو رصد کن
# ═══════════════════════════════════════════════════════════
HOLDINGS = [
    {"name": "تابان",   "aliases": ["تابان"],                "qty": 3697,   "buy_price": None},
    {"name": "پکویر",   "aliases": ["پكوير", "پکویر"],      "qty": 23518,  "buy_price": None},
    {"name": "سمهریز",  "aliases": ["سهرمز", "سمهریز"],     "qty": 5350,   "buy_price": None},
    {"name": "احیا",    "aliases": ["احیا", "احياء"],        "qty": 49122,  "buy_price": None},
    {"name": "پیزد",    "aliases": ["پیزد"],                  "qty": 23220,  "buy_price": None},
    {"name": "خپارس",   "aliases": ["خپارس"],                 "qty": 217948, "buy_price": None},
    {"name": "خگستر",   "aliases": ["خگستر"],                 "qty": 468777, "buy_price": 4327},
    {"name": "فولاد",   "aliases": ["فولاد"],                 "qty": 431948, "buy_price": 3394},
    {"name": "بفجر",    "aliases": ["بفجر"],                  "qty": 0,      "buy_price": None},
]

CHECK_INTERVAL = 30
STATE_FILE = PROJECT_ROOT / "data" / "portfolio_alert_state.json"


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


def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            today = datetime.now().strftime("%Y-%m-%d")
            if data.get("date") == today:
                return data.get("state", {})
        except Exception:
            pass
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "state": state,
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


def check():
    df = att.get_live_market()
    if df is None or df.empty:
        return

    state = load_state()
    now_str = datetime.now().strftime("%H:%M:%S")

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

        # 1. صف خرید جدید
        if buy_q > 0 and sell_q == 0:
            key = symbol + "_BUY_QUEUE"
            if key not in state:
                msg = "🟢 " + symbol + " — صف خرید شد\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                msg += "صف: " + "{:,}".format(int(buy_q)) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    state[key] = now_str
                    print("   [+] " + symbol + " BUY QUEUE")

        # 2. صف فروش جدید
        if sell_q > 0 and buy_q == 0:
            key = symbol + "_SELL_QUEUE"
            if key not in state:
                msg = "🔴 " + symbol + " — صف فروش شد\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + " (" + "{:+.2f}%".format(change) + ")\n"
                msg += "صف: " + "{:,}".format(int(sell_q)) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    state[key] = now_str
                    print("   [-] " + symbol + " SELL QUEUE")

        # 3. تغییر > 5% (بزرگ)
        if abs(change) > 5.0:
            key = symbol + "_BIG_" + ("up" if change > 0 else "down")
            if key not in state:
                emoji = "🚀" if change > 0 else "📉"
                msg = emoji + " " + symbol + " — تغییر بزرگ\n"
                msg += "قیمت: " + "{:,}".format(int(price)) + "\n"
                msg += "تغییر: " + "{:+.2f}%".format(change) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    state[key] = now_str
                    print("   [" + emoji + "] " + symbol)

        # 4. وضعیت فولاد و خگستر (سود/ضرر)
        buy_p = item.get("buy_price")
        if buy_p:
            profit_pct = (price - buy_p) / buy_p * 100
            key = symbol + "_PROFIT_5"
            if profit_pct > 5.0 and key not in state:
                msg = "💰 " + symbol + " — سود بیش از 5%\n"
                msg += "خرید: " + "{:,}".format(int(buy_p)) + "\n"
                msg += "الآن: " + "{:,}".format(int(price)) + "\n"
                msg += "سود: " + "{:+.2f}%".format(profit_pct) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    state[key] = now_str
                    print("   [💰] " + symbol + " PROFIT +5%")

            key_loss = symbol + "_LOSS_5"
            if profit_pct < -5.0 and key_loss not in state:
                msg = "⚠️ " + symbol + " — ضرر بیش از 5%\n"
                msg += "خرید: " + "{:,}".format(int(buy_p)) + "\n"
                msg += "الآن: " + "{:,}".format(int(price)) + "\n"
                msg += "ضرر: " + "{:+.2f}%".format(profit_pct) + "\n"
                msg += "⏰ " + now_str
                if send_eitaa(msg):
                    state[key_loss] = now_str
                    print("   [⚠️] " + symbol + " LOSS -5%")

    save_state(state)


def main():
    print()
    print("=" * 75)
    print("  Smart_Bourse — Portfolio Alert Monitor")
    print("=" * 75)
    print()
    print("  Token: " + (EITAA_TOKEN[:10] + "..." if EITAA_TOKEN else "NOT SET"))
    print("  Chat ID: " + EITAA_CHAT_ID)
    print("  Holdings: " + str(len(HOLDINGS)) + " symbols")
    print()
    for h in HOLDINGS:
        bp = " خرید:" + str(h["buy_price"]) if h.get("buy_price") else ""
        print("     " + h["name"] + " (" + "{:,}".format(h["qty"]) + ")" + bp)
    print()
    print("  Interval: " + str(CHECK_INTERVAL) + "s")
    print("  Market: 9:00 - 12:30")
    print()
    print("  Press Ctrl+C to stop")
    print()

    count = 0
    while True:
        try:
            now_str = datetime.now().strftime("%H:%M:%S")
            if is_market_time():
                check()
                count += 1
                if count % 40 == 0:
                    print("   [" + now_str + "] checked " + str(count) + " times")
            else:
                if count == 0:
                    print("   [" + now_str + "] waiting for market hours...")
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
