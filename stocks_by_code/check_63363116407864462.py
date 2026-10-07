# check_63363116407864462.py
# بررسی آبسال‌ (لابسا)
# INS Code: 63363116407864462
# اجرا: python check_63363116407864462.py

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

INS_CODE = "63363116407864462"
SYMBOL = "لابسا"
SYMBOL_NAME = "آبسال‌"
BUY_PRICE = 0


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


def calc_atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    return float(np.mean(trs[-period:]))


def calc_ma(prices, period):
    if len(prices) < period:
        return None
    return float(np.mean(prices[-period:]))


def get_history_safe(symbol):
    for alias in [symbol, normalize(symbol), SYMBOL, SYMBOL_NAME]:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 15:
                    return df
        except:
            continue
    return None


def fmt_num(val, default="?"):
    if val:
        return f"{int(val):,}"
    return default


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print(f"  📊 بررسی {SYMBOL_NAME} ({SYMBOL})")
    safe_print(f"  🔑 INS Code: {INS_CODE}")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    df = att.get_live_market()
    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    found = None
    for _, row in df.iterrows():
        live_ins = str(row.get("InsCode") or "")
        if live_ins == INS_CODE:
            found = row
            break

    if found is None:
        safe_print(f"  ❌ پیدا نشد! INS: {INS_CODE}")
        return

    safe_print("     ✅ پیدا شد")

    symbol = str(found.get("Symbol", ""))
    name = str(found.get("Name", ""))
    last = float(found.get("Last") or found.get("Close") or 0)
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

    hist = get_history_safe(symbol)
    rsi = None
    atr_pct = None
    ma5 = None
    ma20 = None
    ma50 = None
    closes = []

    if hist is not None:
        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        rsi = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)
        if atr_val and last > 0:
            atr_pct = round((atr_val / last * 100), 2)

        ma5 = calc_ma(closes, 5)
        ma20 = calc_ma(closes, 20)
        ma50 = calc_ma(closes, 50)

    trend = "نامشخص"
    if ma5 and ma20 and ma50:
        if ma5 > ma20 > ma50:
            trend = "صعودی"
        elif ma5 < ma20 < ma50:
            trend = "نزولی"
        else:
            trend = "خنثی"

    safe_print("")
    safe_print(f"  📌 {symbol} — {name}")
    safe_print("")

    safe_print(f"  💰 قیمت‌ها:")
    safe_print(f"     آخرین:      {int(last):>12,}")
    safe_print(f"     دیروز:      {int(yesterday):>12,}")
    safe_print(f"     تغییر:      {change:>11.2f}%")
    safe_print(f"     کف:         {int(min_a):>12,}")
    safe_print(f"     سقف:        {int(max_a):>12,}")

    if BUY_PRICE > 0:
        profit = (last - BUY_PRICE) / BUY_PRICE * 100
        safe_print("")
        safe_print(f"  💰 خرید تو:")
        safe_print(f"     قیمت خرید:  {int(BUY_PRICE):>12,}")
        safe_print(f"     سود/ضرر:    {profit:>11.2f}%")

    safe_print("")

    safe_print(f"  📈 بنیادی:")
    if pe:
        safe_print(f"     P/E:        {pe:>12}")
    safe_print(f"     EPS:        {int(eps):>12,}")
    safe_print("")

    rsi_str = f"{rsi}" if rsi else "?"
    atr_str = f"{atr_pct}%" if atr_pct else "?%"
    ma5_str = fmt_num(ma5)
    ma20_str = fmt_num(ma20)
    ma50_str = fmt_num(ma50)

    safe_print(f"  📉 تکنیکال:")
    safe_print(f"     RSI:        {rsi_str:>12}")
    safe_print(f"     ATR:        {atr_str:>12}")
    safe_print(f"     MA5:        {ma5_str:>12}")
    safe_print(f"     MA20:       {ma20_str:>12}")
    safe_print(f"     MA50:       {ma50_str:>12}")
    safe_print(f"     روند:       {trend:>12}")
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

    safe_print("=" * 100)
    safe_print("  🎯 تصمیم:")
    safe_print("=" * 100)
    safe_print("")

    decision = "🟡 نگه دار"
    reasons = []

    if rsi and rsi > 85:
        decision = "🔴 بفروش (RSI اشباع شدید!)"
        reasons.append(f"RSI={rsi} اشباع شدید")
    elif rsi and rsi > 75:
        decision = "🔴 بفروش (RSI اشباع)"
        reasons.append(f"RSI={rsi} اشباع")
    elif rsi and rsi > 65:
        decision = "🟠 مراقب (RSI بالا)"
        reasons.append(f"RSI={rsi} بالا")
    elif rsi and rsi < 30:
        decision = "🟢 نگه دار (فرصت)"
        reasons.append(f"RSI={rsi} اشباع فروش")

    if has_sell_queue:
        decision = "🔴 بفروش (صف فروش!)"
        reasons.append("صف فروش")
    elif has_buy_queue:
        if decision == "🟡 نگه دار":
            decision = "🟢 نگه دار (صف خرید!)"
        reasons.append("صف خرید")

    if pe and pe > 25:
        reasons.append(f"P/E={pe} گرون")
        if decision == "🟡 نگه دار":
            decision = "🟠 مراقب"

    if trend == "صعودی":
        reasons.append("روند صعودی")
    elif trend == "نزولی":
        reasons.append("روند نزولی")
        if decision == "🟡 نگه دار":
            decision = "🟠 مراقب"

    if vol_sell_n > 0:
        ratio_n = vol_buy_n / vol_sell_n
        if ratio_n < 0.5:
            reasons.append(f"حقوقی فروشنده ({ratio_n:.1f}x)")
            if decision == "🟡 نگه دار":
                decision = "🟠 مراقب"
        elif ratio_n > 2:
            reasons.append(f"حقوقی خریدار ({ratio_n:.1f}x)")

    safe_print(f"  {decision}")
    safe_print("")
    safe_print(f"  📊 دلایل:")
    for r in reasons:
        safe_print(f"     • {r}")
    safe_print("")

    if min_a > 0 and max_a > 0:
        safe_print(f"  💡 استراتژی:")
        safe_print(f"     🟢 خرید:    {int(min_a):>12,}")
        safe_print(f"     🔴 فروش:    {int(max_a):>12,}")
        safe_print(f"     ⛔ حدضرر:   {int(min_a * 0.98):>12,}")

    if rsi and rsi > 80:
        safe_print("")
        safe_print("  🚨 هشدار: RSI اشباع شدید!")

    safe_print("")


if __name__ == "__main__":
    main()
