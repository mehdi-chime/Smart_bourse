
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np


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


def get_rsi(prices, period=14):
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
    return 100 - (100 / (1 + rs))


def get_ma(prices, period):
    if len(prices) < period:
        return None
    return float(np.mean(prices[-period:]))


def get_atr(highs, lows, closes, period=14):
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


def get_bollinger(prices, period=20, std_mult=2):
    if len(prices) < period:
        return None
    recent = prices[-period:]
    ma = float(np.mean(recent))
    std = float(np.std(recent))
    return {
        "upper": ma + std_mult * std,
        "middle": ma,
        "lower": ma - std_mult * std,
    }


def analyze(symbol):
    print()
    print("=" * 75)
    print("  تحليل: " + symbol)
    print("=" * 75)
    print()

    # 1. تاریخچه
    try:
        df = att.get_history(symbol)
    except Exception as e:
        print("  ERROR: " + str(e)[:80])
        return

    if df is None or df.empty or "Close" not in df.columns:
        print("  no data")
        return

    closes = df["Close"].tolist()[-250:]
    highs = df["High"].tolist()[-250:] if "High" in df.columns else closes
    lows = df["Low"].tolist()[-250:] if "Low" in df.columns else closes

    price = closes[-1]

    # 2. داده‌ی زنده
    try:
        live = att.get_live_market()
        r = live[live["Symbol"] == symbol]
        if r.empty:
            r = live[live["Symbol"].apply(lambda x: normalize(x)) == normalize(symbol)]
        r = r.iloc[0] if not r.empty else None
    except Exception:
        r = None

    if r is None:
        print("  cannot find " + symbol + " in live market")
        return

    last = float(r.get("Last") or 0)
    close = float(r.get("Close") or 0)
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

    # 3. اندیکاتورها
    rsi = get_rsi(closes, 14)
    ma20 = get_ma(closes, 20)
    ma50 = get_ma(closes, 50)
    atr_val = get_atr(highs[-60:], lows[-60:], closes[-60:], 14)
    bb = get_bollinger(closes, 20, 2)

    # 4. امتیازدهی

    # RSI
    rsi_score = 0
    rsi_reason = ""
    if rsi:
        if rsi >= 99:
            rsi_score = -2
            rsi_reason = "RSI " + str(round(rsi, 1)) + " — قفل صف خرید (خیلی بالا)"
        elif rsi >= 80:
            rsi_score = -2
            rsi_reason = "RSI " + str(round(rsi, 1)) + " — اشباع شدید"
        elif rsi >= 70:
            rsi_score = -1
            rsi_reason = "RSI " + str(round(rsi, 1)) + " — اشباع خرید"
        elif rsi >= 55:
            rsi_score = 1
            rsi_reason = "RSI " + str(round(rsi, 1)) + " — نرمال مثبت"
        elif rsi >= 45:
            rsi_score = 0
            rsi_reason = "RSI " + str(round(rsi, 1)) + " — نرمال"
        elif rsi >= 30:
            rsi_score = 1
            rsi_reason = "RSI " + str(round(rsi, 1)) + " — نزدیک اشباع فروش"
        else:
            rsi_score = 2
            rsi_reason = "RSI " + str(round(rsi, 1)) + " — اشباع فروش (فرصت خرید)"

    # نسبت خرید/فروش
    ratio_score = 0
    ratio_reason = ""
    if ratio >= 999:
        ratio_score = 2
        ratio_reason = "فروش حقیقی صفر — فشار خرید شدید"
    elif ratio >= 5:
        ratio_score = 2
        ratio_reason = "نسبت " + str(round(ratio, 2)) + " — فشار خرید قوی"
    elif ratio >= 2:
        ratio_score = 1
        ratio_reason = "نسبت " + str(round(ratio, 2)) + " — خرید حقیقی"
    elif ratio >= 1:
        ratio_score = 0
        ratio_reason = "نسبت " + str(round(ratio, 2)) + " — متعادل"
    elif ratio >= 0.5:
        ratio_score = -1
        ratio_reason = "نسبت " + str(round(ratio, 2)) + " — فروش حقیقی"
    else:
        ratio_score = -2
        ratio_reason = "نسبت " + str(round(ratio, 2)) + " — فشار فروش"

    # صف
    queue_score = 0
    queue_reason = ""
    if buy_q > 0 and sell_q == 0:
        queue_score = 2
        queue_reason = "صف خرید — تقاضای قوی"
    elif sell_q > 0 and buy_q == 0:
        queue_score = -2
        queue_reason = "صف فروش — فشار عرضه"
    else:
        queue_score = 0
        queue_reason = "بدون صف — بازار آزاد"

    # روند
    trend_score = 0
    trend_reason = ""
    if ma20 and ma50:
        if last > ma20 > ma50:
            trend_score = 1
            trend_reason = "روند صعودی"
        elif last < ma20 < ma50:
            trend_score = -1
            trend_reason = "روند نزولی"
        else:
            trend_score = 0
            trend_reason = "روند مختلط"

    # Bollinger
    bb_score = 0
    bb_reason = ""
    if bb:
        if last < bb["lower"]:
            bb_score = 2
            bb_reason = "زیر Bollinger — فرصت خرید"
        elif last > bb["upper"]:
            bb_score = -2
            bb_reason = "بالای Bollinger — احتمال اصلاح"
        else:
            bb_score = 0
            bb_reason = "داخل Bollinger — نرمال"

    # آخر وقت
    candle_score = 0
    candle_reason = ""
    if close > 0 and last > 0:
        diff_pct = (last - close) / close * 100
        if diff_pct > 1:
            candle_score = 1
            candle_reason = "آخرین > پایانی (+" + str(round(diff_pct, 2)) + "%) — تقاضای آخر وقت"
        elif diff_pct < -1:
            candle_score = -1
            candle_reason = "آخرین < پایانی (" + str(round(diff_pct, 2)) + "%) — فروش آخر وقت"
        else:
            candle_score = 0
            candle_reason = "آخرین ≈ پایانی — تعادل"

    # 5. جمع امتیاز
    total = rsi_score + ratio_score + queue_score + trend_score + bb_score + candle_score

    # 6. نمایش
    print("  داده:")
    print("     آخرین: " + "{:,}".format(int(last)))
    print("     پایانی: " + "{:,}".format(int(close)))
    print("     تغییر: " + "{:+.2f}%".format(change))
    print("     نسبت خرید: " + "{:.2f}".format(ratio))
    print("     خرید حقیقی: " + "{:,}".format(int(vol_buy)))
    print("     فروش حقیقی: " + "{:,}".format(int(vol_sell)))
    print()

    print("  امتیازها:")
    print("     RSI        (" + str(rsi_score).rjust(3) + "): " + rsi_reason)
    print("     نسبت خرید  (" + str(ratio_score).rjust(3) + "): " + ratio_reason)
    print("     صف          (" + str(queue_score).rjust(3) + "): " + queue_reason)
    print("     روند        (" + str(trend_score).rjust(3) + "): " + trend_reason)
    print("     Bollinger  (" + str(bb_score).rjust(3) + "): " + bb_reason)
    print("     آخر وقت    (" + str(candle_score).rjust(3) + "): " + candle_reason)
    print()

    print("  ─────────────────────────────────────")
    print("  امتیاز کل: " + str(total) + "  (از -12 تا +12)")
    print("  ─────────────────────────────────────")
    print()

    # 7. تصمیم
    if total >= 5:
        decision = "🟢🟢 بخر (قوی)"
        color = "BUY_STRONG"
    elif total >= 3:
        decision = "🟢 بخر"
        color = "BUY"
    elif total >= 1:
        decision = "🟡 نگه دار (مثبت)"
        color = "HOLD_POSITIVE"
    elif total >= -1:
        decision = "⚪ صبر کن"
        color = "WAIT"
    elif total >= -3:
        decision = "🟡 نگه دار (منفی)"
        color = "HOLD_NEGATIVE"
    elif total >= -5:
        decision = "🔴 بفروش"
        color = "SELL"
    else:
        decision = "🔴🔴 بفروش فوری"
        color = "SELL_STRONG"

    print("  🎯 تصمیم: " + decision)
    print()

    # 8. قیمت‌های کلیدی
    if atr_val:
        stop = last - 2 * atr_val
        target_1 = last + 1.5 * atr_val
        target_2 = last + 3 * atr_val
        print("  💰 قیمت‌های کلیدی:")
        print("     حد ضرر: " + "{:,}".format(int(stop)))
        print("     هدف 1: " + "{:,}".format(int(target_1)))
        print("     هدف 2: " + "{:,}".format(int(target_2)))
        print()
        print("  📊 نوسان (ATR): " + "{:.0f}".format(atr_val) + " (" + "{:.2f}%".format(atr_val / last * 100) + ")")
        print()

    print("  ⏰ " + datetime.now().strftime("%H:%M:%S"))
    print()


if __name__ == "__main__":
    print()
    print("=" * 75)
    print("  Smart_Bourse — Decision Maker")
    print("=" * 75)

    # سهم‌های پرتفوی
    symbols = ["پكوير", "فولاد", "خگستر", "خپارس", "پیزد", "سمهریز", "احیا", "تابان"]

    for s in symbols:
        try:
            analyze(s)
        except Exception as e:
            print("  error on " + s + ": " + str(e)[:80])
            print()
