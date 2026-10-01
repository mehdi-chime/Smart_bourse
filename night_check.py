# night_check.py
# بررسی شبانه پرتفوی
# اجرا: python night_check.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# ✅ UTF-8
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


def send_eitaa(text):
    """ارسال به ایتا"""
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


def analyze(symbol, buy_price=None):
    """تحلیل کامل با سود/ضرر"""
    r = {"symbol": symbol, "found": False}

    try:
        df = att.get_live_market()
        if df is None or df.empty:
            r["error"] = "Live data error"
            return r

        if "InstrumentType" in df.columns:
            df = df[df["InstrumentType"] == 300]

        found = None
        for _, row in df.iterrows():
            if normalize(str(row.get("Symbol", ""))) == normalize(symbol):
                found = row
                break

        if found is None:
            r["error"] = "Not found"
            return r

        r["found"] = True
        r["name"] = str(found.get("Name", ""))

        last = float(found.get("Last") or 0)
        yesterday = float(found.get("Yesterday") or 0)
        min_a = float(found.get("MinAllowed") or 0)
        max_a = float(found.get("MaxAllowed") or 0)
        change = float(found.get("ChangePct") or 0)
        eps = float(found.get("EPS") or 0)

        r["last"] = last
        r["yesterday"] = yesterday
        r["min_a"] = min_a
        r["max_a"] = max_a
        r["change"] = change
        r["eps"] = eps

        if eps > 0:
            r["pe"] = round(last / eps, 2)

        # حقوقی
        r["vol_buy_n"] = float(found.get("Vol_buy_institutional") or 0)
        r["vol_sell_n"] = float(found.get("Vol_sell_institutional") or 0)

        # صف
        bid_v1 = float(found.get("BidVolume1") or 0)
        ask_v1 = float(found.get("AskVolume1") or 0)
        r["has_buy_queue"] = (ask_v1 == 0 and bid_v1 > 0)
        r["has_sell_queue"] = (bid_v1 == 0 and ask_v1 > 0)

        # سود/ضرر
        if buy_price and buy_price > 0:
            r["buy_price"] = buy_price
            r["profit_pct"] = round((last - buy_price) / buy_price * 100, 2)

    except Exception as e:
        r["error"] = str(e)
        return r

    # RSI + ATR
    try:
        hist = get_history_safe(symbol)
        if hist is not None:
            closes = hist["Close"].tolist()
            highs = hist["High"].tolist() if "High" in hist.columns else closes
            lows = hist["Low"].tolist() if "Low" in hist.columns else closes

            r["rsi"] = calc_rsi(closes, 14)
            atr_val = calc_atr(highs, lows, closes, 14)
            if atr_val and last > 0:
                r["atr_pct"] = round((atr_val / last * 100), 2)
    except:
        pass

    # تصمیم
    decision = "🟡 نگه دار"
    reasons = []

    # سود/ضرر
    if buy_price:
        profit = r.get("profit_pct", 0)

        if profit <= -5:
            decision = "🔴 بفروش (حد ضرر)"
            reasons.append(f"ضرر {profit:.1f}%")
        elif profit >= 5:
            decision = "🟢 بفروش (سود خوب)"
            reasons.append(f"سود {profit:.1f}%")
        elif profit <= -3:
            decision = "🟠 هشدار (ضرر)"
            reasons.append(f"ضرر {profit:.1f}%")
        elif profit >= 3:
            decision = "🟢 فرصت فروش"
            reasons.append(f"سود {profit:.1f}%")

    # RSI
    rsi = r.get("rsi")
    if rsi:
        if rsi > 75:
            decision = "🔴 بفروش (اشباع)"
            reasons.append(f"RSI={rsi}")
        elif rsi < 25:
            decision = "🟢 نگه دار (فرصت)"
            reasons.append(f"RSI={rsi}")

    # صف
    if r.get("has_sell_queue"):
        decision = "🔴 بفروش (صف فروش)"
        reasons.append("صف فروش")
    elif r.get("has_buy_queue"):
        reasons.append("صف خرید")

    r["decision"] = decision
    r["reasons"] = reasons

    return r


def print_result(r):
    safe_print("")
    safe_print("=" * 80)

    if r.get("error"):
        safe_print(f"  ❌ {r['symbol']}: {r['error']}")
        safe_print("=" * 80)
        return

    safe_print(f"  📊 {r['symbol']} - {r.get('name', '')}")
    safe_print("=" * 80)
    safe_print("")

    safe_print(f"  💰 قیمت فعلی: {int(r['last']):,}")
    safe_print(f"  📊 تغییر: {r['change']:+.2f}%")

    if r.get("buy_price"):
        profit = r.get("profit_pct", 0)
        emoji = "🟢" if profit > 0 else "🔴"
        safe_print(f"  {emoji} خرید تو: {int(r['buy_price']):,}")
        safe_print(f"  {emoji} سود/ضرر: {profit:+.2f}%")

    if r.get("pe"):
        safe_print(f"  📈 P/E: {r['pe']}")

    if r.get("rsi"):
        safe_print(f"  📉 RSI: {r['rsi']}")

    if r.get("atr_pct"):
        safe_print(f"  📊 ATR: {r['atr_pct']}%")

    if r.get("vol_sell_n", 0) > 0:
        ratio = r["vol_buy_n"] / r["vol_sell_n"]
        if ratio > 1.5:
            safe_print(f"  🟢 حقوقی: خریدار")
        elif ratio < 0.7:
            safe_print(f"  🔴 حقوقی: فروشنده")

    safe_print("")
    safe_print(f"  🎯 تصمیم: {r['decision']}")

    if r.get("reasons"):
        safe_print(f"  📊 دلایل:")
        for reason in r["reasons"]:
            safe_print(f"     • {reason}")

    safe_print("")
    safe_print("=" * 80)


def build_eitaa_msg(results):
    """پیام ایتا"""
    msg = f"🌙 بررسی شبانه\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for r in results:
        if not r.get("found"):
            continue

        msg += f"📌 {r['symbol']}\n"
        msg += f"💰 {int(r['last']):,} ({r['change']:+.2f}%)\n"

        if r.get("buy_price"):
            profit = r.get("profit_pct", 0)
            emoji = "🟢" if profit > 0 else "🔴"
            msg += f"{emoji} سود: {profit:+.2f}%\n"

        if r.get("rsi"):
            msg += f"📉 RSI: {r['rsi']}\n"

        msg += f"🎯 {r['decision']}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    return msg


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  🌙 بررسی شبانه - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    safe_print("=" * 80)
    safe_print("")

    # پرتفوی با قیمت خرید
    PORTFOLIO = [
        {"symbol": "فولاد", "buy_price": 0},      # بلندمدت
        {"symbol": "تابان", "buy_price": 0},      # ??
        {"symbol": "احیا", "buy_price": 0},       # ??
        {"symbol": "سمهریز", "buy_price": 0},     # ??
        {"symbol": "رتاپ", "buy_price": 9060},    # خرید تو
        {"symbol": "خگستر", "buy_price": 0},      # ??
        {"symbol": "خپارس", "buy_price": 0},      # ??
    ]

    safe_print("  📋 پرتفوی تو:")
    safe_print("")

    for p in PORTFOLIO:
        sym = p["symbol"]
        bp = p.get("buy_price", 0)
        bp_str = f"{bp:,}" if bp > 0 else "?"
        safe_print(f"     {sym}: خرید {bp_str}")

    safe_print("")
    safe_print("  🔍 تحلیل...")
    safe_print("")

    results = []
    for p in PORTFOLIO:
        sym = p["symbol"]
        bp = p.get("buy_price", 0)
        safe_print(f"  {sym}...")
        r = analyze(sym, bp if bp > 0 else None)
        results.append(r)
        print_result(r)

    # ارسال به ایتا
    safe_print("")
    safe_print("  📱 ارسال به ایتا...")
    msg = build_eitaa_msg(results)
    if send_eitaa(msg):
        safe_print("  ✅ ارسال شد")
    else:
        safe_print("  ❌ خطا")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
