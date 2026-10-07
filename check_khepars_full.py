# check_khepars_full.py
# بررسی کامل خپارس (لغو پذیرش)
# اجرا: python check_khepars_full.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np

# INS Code خپارس
KHEPARS_INS = "25211433301660888"  # ← از اسکرین‌شات


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    p = np.array(prices, dtype=float)
    deltas = np.diff(p)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    ag = gains[-period:].mean()
    al = losses[-period:].mean()
    if al == 0 and ag > 0:
        return 100
    if al == 0 and ag == 0:
        return 50
    rs = ag / al
    return round(100 - (100 / (1 + rs)), 1)


def get_history_safe(symbol):
    for alias in [symbol, "خپارس", "خپارس"]:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 15:
                    return df
        except:
            continue
    return None


def send_eitaa(text):
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
        import requests
        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=15)
        return r.status_code == 200
    except:
        return False


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🔴 بررسی خپارس — لغو پذیرش!")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    # دریافت داده
    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    # پیدا کردن خپارس
    found = None
    for _, row in df.iterrows():
        ins = str(row.get("InsCode") or "")
        symbol = str(row.get("Symbol", ""))

        if ins == KHEPARS_INS or symbol == "خپارس" or symbol == "خپارس":
            found = row
            break

    if found is None:
        safe_print("  ❌ خپارس پیدا نشد!")
        safe_print("")
        safe_print("  📌 جستجو در همه:")
        for _, row in df.iterrows():
            symbol = str(row.get("Symbol", ""))
            if "خپ" in symbol or "پارس" in symbol:
                safe_print(f"     - {symbol} | {row.get('Name')} | {row.get('InsCode')}")
        return

    safe_print("     ✅ پیدا شد")

    # اطلاعات
    symbol = str(found.get("Symbol", ""))
    name = str(found.get("Name", ""))
    last = float(found.get("Last") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    change = float(found.get("ChangePct") or 0)
    eps = float(found.get("EPS") or 0)

    # P/E
    pe = None
    if eps > 0:
        pe = round(last / eps, 2)

    # سفارشات
    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

    # صف
    bid_v1 = float(found.get("BidVolume1") or 0)
    ask_v1 = float(found.get("AskVolume1") or 0)
    has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
    has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

    # RSI
    hist = get_history_safe(symbol)
    rsi = None
    if hist is not None:
        closes = hist["Close"].tolist()
        rsi = calc_rsi(closes, 14)

    # نمایش
    safe_print("")
    safe_print(f"  📌 {symbol} — {name}")
    safe_print("")

    safe_print(f"  💰 قیمت‌ها:")
    safe_print(f"     آخرین:      {int(last):>12,}")
    safe_print(f"     دیروز:      {int(yesterday):>12,}")
    safe_print(f"     تغییر:      {change:>11.2f}%")
    safe_print(f"     کف:         {int(min_a):>12,}")
    safe_print(f"     سقف:        {int(max_a):>12,}")
    safe_print("")

    safe_print(f"  📈 بنیادی:")
    if pe:
        safe_print(f"     P/E:        {pe:>12}")
    safe_print(f"     EPS:        {int(eps):>12,}")
    safe_print("")

    safe_print(f"  📉 تکنیکال:")
    safe_print(f"     RSI:        {rsi if rsi else '?':>12}")
    safe_print("")

    safe_print(f"  🏛️ سفارشات:")
    safe_print(f"     حقیقی خرید:  {int(vol_buy):>12,}")
    safe_print(f"     حقیقی فروش:  {int(vol_sell):>12,}")
    safe_print(f"     حقوقی خرید:  {int(vol_buy_n):>12,}")
    safe_print(f"     حقوقی فروش:  {int(vol_sell_n):>12,}")
    safe_print("")

    if has_buy_queue:
        safe_print("  🟢 صف خرید")
    elif has_sell_queue:
        safe_print("  🔴 صف فروش")
    safe_print("")

    # تصمیم
    safe_print("=" * 100)
    safe_print("  🎯 تصمیم (بر اساس لغو پذیرش):")
    safe_print("=" * 100)
    safe_print("")

    safe_print("  🔴 بفروش! (اولویت بالا)")
    safe_print("")
    safe_print("  📊 دلایل:")
    safe_print("     ❌ لغو پذیرش از بورس")
    safe_print("     ❌ بازار پایه زرد فرابورس")
    safe_print("     ❌ نقدشوندگی کم")
    safe_print("     ❌ ریسک حذف کامل")
    safe_print(f"     ❌ منفی {change:.2f}%")
    safe_print(f"     ❌ فروش حقیقی ۹۵.۸٪")
    safe_print("")

    safe_print("  ⚠️ هشدار:")
    safe_print("     اگه امروز نفروشی، ممکنه:")
    safe_print("     - صف فروش بشه")
    safe_print("     - نتونی بفروشی")
    safe_print("     - بیشتر ضرر کنی")
    safe_print("")

    # ایتا
    safe_print("  📱 ارسال به ایتا...")

    msg = f"🔴 هشدار خپارس\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg += f"⚠️ لغو پذیرش از بورس\n"
    msg += f"💰 {int(last):,} ({change:+.2f}%)\n"
    msg += f"📊 بازار پایه زرد فرابورس\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🎯 پیشنهاد: بفروش!\n"

    if send_eitaa(msg):
        safe_print("     ✅ ارسال شد")
    else:
        safe_print("     ❌ خطا")
    safe_print("")


if __name__ == "__main__":
    main()
