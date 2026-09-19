"""
Project : Smart_Bourse
File    : scanner/deep_analyzer.py
Version : 1.0.0
Description :
    تحلیل عمیق یه سهم
    - RSI، حمایت/مقاومت
    - بک‌تست استراتژی -3%/+3%
    - وضعیت فعلی (صف، حقوقی/حقیقی)
"""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np
import pandas as pd


# ======================================================================
# تنظیمات
# ======================================================================

SYMBOL = "خگستر"   # ← می‌تونی عوض کنی
BUY_THRESHOLD = -3.0   # خرید در -3%
SELL_THRESHOLD = 3.0   # فروش در +3%
HOLD_DAYS = 1          # چند روز نگه داریم


# ======================================================================
# محاسبات
# ======================================================================

def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    prices = np.array(prices, dtype=float)
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    ag = gains[-period:].mean()
    al = losses[-period:].mean()
    if al == 0:
        return 100.0
    rs = ag / al
    return round(100 - 100 / (1 + rs), 2)


def find_support_resistance(prices, lookback=60):
    """پیدا کردن حمایت و مقاومت"""
    if len(prices) < lookback:
        lookback = len(prices)
    recent = prices[-lookback:]
    return {
        "min": min(recent),
        "max": max(recent),
        "avg": sum(recent) / len(recent),
    }


def backtest_minus3_strategy(df):
    """بک‌تست استراتژی: خرید در -3%، فروش در +3% (یا بعد از N روز)"""
    if df is None or df.empty or "Close" not in df.columns:
        return None

    # محاسبه تغییر درصدی روزانه
    df = df.copy()
    df["pct_change"] = df["Close"].pct_change() * 100

    trades = []
    i = 1
    while i < len(df) - HOLD_DAYS:
        change = df["pct_change"].iloc[i]

        # اگه -3% یا کمتر افتاد، بخر
        if change is not None and change <= BUY_THRESHOLD:
            buy_price = df["Close"].iloc[i]
            sell_idx = i + HOLD_DAYS
            if sell_idx < len(df):
                sell_price = df["Close"].iloc[sell_idx]
                profit_pct = (sell_price - buy_price) / buy_price * 100
                trades.append({
                    "buy_idx": i,
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "profit_pct": profit_pct,
                })
                i = sell_idx + 1
                continue
        i += 1

    return trades


# ======================================================================
# تحلیل
# ======================================================================

def analyze(symbol):
    print()
    print("=" * 70)
    print("  تحلیل عمیق: " + symbol)
    print("=" * 70)

    # تاریخچه
    print()
    print("📡 دریافت تاریخچه ...")
    try:
        df = att.get_history(symbol)
    except Exception as e:
        print("خطا: " + str(e))
        return

    if df is None or df.empty:
        print("داده‌ای نیست")
        return

    prices = df["Close"].tolist()
    volumes = df["Volume"].tolist() if "Volume" in df.columns else []

    # قیمت فعلی
    last_price = prices[-1]
    first_price_30d = prices[-30] if len(prices) >= 30 else prices[0]
    change_30d = (last_price - first_price_30d) / first_price_30d * 100

    # RSI
    rsi = calc_rsi(prices)

    # حمایت/مقاومت
    sr = find_support_resistance(prices, lookback=60)

    # تغییرات اخیر
    last_5 = df.tail(5)
    last_5_changes = []
    if "Close" in last_5.columns:
        pct = last_5["Close"].pct_change() * 100
        last_5_changes = [round(x, 2) if not pd.isna(x) else 0 for x in pct.tolist()]

    # بک‌تست استراتژی
    bt = backtest_minus3_strategy(df)

    # ============================================================
    # گزارش
    # ============================================================

    print()
    print("─" * 70)
    print("  📊 قیمت و روند")
    print("─" * 70)
    print("   قیمت فعلی       : " + "{:,}".format(int(last_price)))
    print("   میانگین 60 روز  : " + "{:,}".format(int(sr["avg"])))
    print("   حمایت (کف)      : " + "{:,}".format(int(sr["min"])))
    print("   مقاومت (سقف)    : " + "{:,}".format(int(sr["max"])))
    print("   تغییر 30 روز    : " + "{:+.2f}%".format(change_30d))

    print()
    print("─" * 70)
    print("  📈 اندیکاتورها")
    print("─" * 70)
    if rsi:
        rsi_status = "اشباع خرید ⚠️" if rsi > 70 else "اشباع فروش 🟢" if rsi < 30 else "نرمال"
        print("   RSI (14)         : " + str(rsi) + "  " + rsi_status)

    print("   5 روز اخیر       : " + " | ".join(["{:+.2f}%".format(x) for x in last_5_changes[1:]]))

    # موقعیت فعلی
    print()
    print("─" * 70)
    print("  🎯 موقعیت فعلی")
    print("─" * 70)
    if last_price <= sr["avg"]:
        print("   زیر میانگین 60 روز → فرصت خرید نسبی")
    else:
        print("   بالای میانگین 60 روز → احتیاط")

    # فاصله تا حمایت/مقاومت
    dist_support = (last_price - sr["min"]) / sr["min"] * 100
    dist_resist = (sr["max"] - last_price) / last_price * 100
    print("   فاصله تا حمایت   : " + "{:.2f}%".format(dist_support))
    print("   فاصله تا مقاومت  : " + "{:.2f}%".format(dist_resist))

    # بک‌تست
    if bt:
        profits = [t["profit_pct"] for t in bt]
        wins = [p for p in profits if p > 0]
        win_rate = len(wins) / len(bt) * 100
        avg = sum(profits) / len(bt)

        print()
        print("─" * 70)
        print("  🔬 بک‌تست استراتژی: خرید در -3%، فروش بعد " + str(HOLD_DAYS) + " روز")
        print("─" * 70)
        print("   تعداد فرصت‌ها    : " + str(len(bt)))
        print("   نرخ برد          : " + "{:.1f}%".format(win_rate))
        print("   میانگین سود      : " + "{:+.2f}%".format(avg))
        print("   بهترین معامله   : " + "{:+.2f}%".format(max(profits)))
        print("   بدترین معامله   : " + "{:+.2f}%".format(min(profits)))

        # نتیجه‌گیری
        print()
        if win_rate > 55:
            print("   ✅ استراتژی خوبی داری!")
        elif win_rate > 45:
            print("   🟡 استراتژی متوسطه — حد ضرر بذار")
        else:
            print("   🔴 استراتژی پرریسک — حتماً حد ضرر بذار")
    else:
        print()
        print("   ⚠️  بک‌تست امکان‌پذیر نبود (داده کافی نیست)")

    # تاریخچه اخیر
    print()
    print("─" * 70)
    print("  📅 ۱۰ روز اخیر")
    print("─" * 70)
    print("   تاریخ      |    قیمت    |  تغییر")
    print("   " + "-" * 50)
    for i in range(max(-10, -len(df)), 0):
        try:
            date = df.index[i]
            close = df["Close"].iloc[i]
            change = df["Close"].pct_change().iloc[i] * 100
            print("   " + str(date).ljust(11) + " | " + "{:,}".format(int(close)).rjust(9) + " | " + "{:+.2f}%".format(change))
        except Exception:
            pass

    print()
    print("=" * 70)
    print("   پایان تحلیل")
    print("=" * 70)


# ======================================================================

if __name__ == "__main__":
    analyze(SYMBOL)
