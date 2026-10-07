# check_hafari.py
# بررسی حفاری بعد از ۲ روز منفی
# اجرا: python check_hafari.py

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


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def normalize(s):
    if not s:
        return s
    return (str(s)
            .replace("\u0643", "\u06a9")
            .replace("\u064a", "\u06cc")
            .replace("\u0649", "\u06cc")
            .replace("\u0629", "\u0647")
            .replace("\u0640", "")
            .replace(" ", "")
            .strip())


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
    for alias in [symbol, normalize(symbol), "حفاری", "حفاري"]:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 15:
                    return df
        except:
            continue
    return None


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🔍 بررسی حفاری (بعد از ۲ روز منفی)")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    df = att.get_live_market()
    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    # پیدا کردن
    found = None
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if normalize("حفاري") == normalize(symbol):
            found = row
            break

    if found is None:
        safe_print("  ❌ حفاری پیدا نشد!")
        return

    # اطلاعات
    symbol = str(found.get("Symbol", ""))
    name = str(found.get("Name", ""))
    last = float(found.get("Last") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    change = float(found.get("ChangePct") or 0)
    eps = float(found.get("EPS") or 0)

    pe = None
    if eps > 0:
        pe = round(last / eps, 2)

    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

    bid_v1 = float(found.get("BidVolume1") or 0)
    ask_v1 = float(found.get("AskVolume1") or 0)
    has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
    has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

    ratio = 1.0
    if vol_sell > 0:
        ratio = round(vol_buy / vol_sell, 2)

    # تاریخچه
    hist = get_history_safe(symbol)
    rsi = None
    closes = []

    if hist is not None:
        closes = hist["Close"].tolist()
        rsi = calc_rsi(closes, 14)

    # نمایش
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
    safe_print(f"     نسبت:        {ratio:>12}")
    safe_print("")

    if has_buy_queue:
        safe_print("  🟢 صف خرید")
    elif has_sell_queue:
        safe_print("  🔴 صف فروش")
    safe_print("")

    # تاریخچه ۷ روز
    if len(closes) >= 7:
        safe_print("  📊 ۷ روز اخیر:")
        recent = closes[-7:]
        for i, c in enumerate(recent, 1):
            day_ch = 0
            if i > 1:
                day_ch = (c - recent[i-2]) / recent[i-2] * 100
            emoji = "🟢" if day_ch >= 0 else "🔴"
            safe_print(f"     {emoji} {int(c):>10,} ({day_ch:+.2f}%)")
        safe_print("")

        neg = sum(1 for i in range(1, len(recent)) if recent[i] < recent[i-1])
        safe_print(f"     منفی: {neg}/۶ روز")

    # ذخیره
    output = PROJECT_ROOT / "reports" / f"hafari_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "last": last,
            "change": change,
            "pe": pe,
            "rsi": rsi,
            "ratio": ratio,
        }, f, ensure_ascii=False, indent=2)

    safe_print("")
    safe_print(f"  💾 ذخیره: {output}")
    safe_print("")


if __name__ == "__main__":
    main()
