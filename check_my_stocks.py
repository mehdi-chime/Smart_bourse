# check_my_stocks.py
# بررسی سهم‌های من — بدون input
# اجرا: python check_my_stocks.py

import os
import sys
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

# ═══════════════════════════════════════════════════════════
# اینجا سهم‌هایی که می‌خوای بررسی کنی رو بذار
# ═══════════════════════════════════════════════════════════

STOCKS = [
    "فولاد",
    "خودرو",
    "وبملت",
    "شپنا",
    "خگستر",
    "شتران",
    "فملی",
    "کگل",
]


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
    for alias in [symbol, normalize(symbol)]:
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
    safe_print("  📊 بررسی سهم‌های من")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    # دریافت
    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    # بررسی هر سهم
    results = []

    for stock_name in STOCKS:
        safe_print(f"  🔍 بررسی {stock_name}...")

        # پیدا کردن
        found = None
        for _, row in df.iterrows():
            symbol = str(row.get("Symbol", ""))
            if normalize(stock_name) == normalize(symbol):
                found = row
                break

        if found is None:
            safe_print(f"     ❌ پیدا نشد")
            safe_print("")
            continue

        # اطلاعات
        symbol = str(found.get("Symbol", ""))
        name = str(found.get("Name", ""))
        last = float(found.get("Last") or found.get("Close") or 0)
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

        results.append({
            "symbol": symbol,
            "name": name,
            "last": last,
            "change": change,
            "pe": pe,
            "rsi": rsi,
            "atr_pct": atr_pct,
            "trend": trend,
            "ratio": ratio,
            "has_buy_queue": has_buy_queue,
            "has_sell_queue": has_sell_queue,
            "vol_buy_n": vol_buy_n,
            "vol_sell_n": vol_sell_n,
            "min_a": min_a,
            "max_a": max_a,
            "ma5": ma5,
            "ma20": ma20,
            "ma50": ma50,
        })

        safe_print(f"     ✅ پیدا شد")
        safe_print("")

    # نمایش جدول
    safe_print("=" * 100)
    safe_print("  📊 جدول کلی")
    safe_print("=" * 100)
    safe_print("")
    safe_print(f"  {'#':<3} | {'نماد':<10} | {'قیمت':>10} | {'تغییر':>7} | {'P/E':>5} | {'RSI':>5} | {'روند':>7} | {'صف':>5}")
    safe_print("  " + "-" * 90)

    for i, r in enumerate(results, 1):
        queue = "BUY" if r['has_buy_queue'] else ("SELL" if r['has_sell_queue'] else "---")
        rsi_str = f"{r['rsi']:.1f}" if r['rsi'] else "?"
        pe_str = f"{r['pe']}" if r['pe'] else "?"

        safe_print(
            f"  {i:<3} | "
            f"{r['symbol'][:10]:<10} | "
            f"{int(r['last']):>10,} | "
            f"{r['change']:>6.2f}% | "
            f"{pe_str:>5} | "
            f"{rsi_str:>5} | "
            f"{r['trend'][:7]:>7} | "
            f"{queue:>5}"
        )

    safe_print("")

    # جزئیات
    for i, r in enumerate(results, 1):
        safe_print("=" * 100)
        safe_print(f"  {i}. {r['symbol']} — {r['name']}")
        safe_print("=" * 100)
        safe_print("")

        safe_print(f"  💰 قیمت: {int(r['last']):,} ({r['change']:+.2f}%)")

        if r['pe']:
            safe_print(f"  📈 P/E: {r['pe']}")

        rsi_str = f"{r['rsi']}" if r['rsi'] else "?"
        atr_str = f"{r['atr_pct']}%" if r['atr_pct'] else "?%"
        safe_print(f"  📉 RSI: {rsi_str} | ATR: {atr_str}")
        safe_print(f"  📊 MA5: {fmt_num(r['ma5'])} | MA20: {fmt_num(r['ma20'])} | MA50: {fmt_num(r['ma50'])}")
        safe_print(f"  📊 روند: {r['trend']} | نسبت: {r['ratio']}")

        if r['has_buy_queue']:
            safe_print(f"  🟢 صف خرید")
        elif r['has_sell_queue']:
            safe_print(f"  🔴 صف فروش")

        # تصمیم
        rsi = r['rsi']
        decision = "🟡 نگه دار"

        if rsi and rsi > 85:
            decision = "🔴 بفروش (RSI اشباع شدید!)"
        elif rsi and rsi > 75:
            decision = "🔴 بفروش (RSI اشباع)"
        elif rsi and rsi < 30:
            decision = "🟢 نگه دار (فرصت)"

        if r['has_sell_queue']:
            decision = "🔴 بفروش (صف فروش!)"
        elif r['has_buy_queue'] and decision == "🟡 نگه دار":
            decision = "🟢 نگه دار (صف خرید!)"

        safe_print(f"  🎯 {decision}")

        if r['min_a'] > 0 and r['max_a'] > 0:
            profit = (r['max_a'] / r['min_a'] - 1) * 100 - 1.25
            safe_print(f"  💡 خرید: {int(r['min_a']):,} | فروش: {int(r['max_a']):,} | سود: {profit:.2f}%")

        safe_print("")

    safe_print("=" * 100)
    safe_print("  ✅ تمام!")
    safe_print("=" * 100)
    safe_print("")


if __name__ == "__main__":
    main()
