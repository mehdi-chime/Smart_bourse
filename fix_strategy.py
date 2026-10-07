# fix_strategy.py
# بازسازی استراتژی بر اساس درس‌های فولاد
# اجرا: python fix_strategy.py

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
    for alias in [symbol, normalize(symbol)]:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 15:
                    return df
        except:
            continue
    return None


def analyze_stock_v2(row):
    """تحلیل با استراتژی جدید — صف خرید مهم‌تره"""
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol:
            return None

        last = float(row.get("Last") or row.get("Close") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0:
            return None

        # صف
        bid_v1 = float(row.get("BidVolume1") or 0)
        ask_v1 = float(row.get("AskVolume1") or 0)
        has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
        has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

        # سفارشات
        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        # P/E
        pe = None
        if eps > 0:
            pe = round(last / eps, 2)

        # RSI
        hist = get_history_safe(symbol)
        rsi = None
        if hist is not None:
            closes = hist["Close"].tolist()
            rsi = calc_rsi(closes, 14)

        # نسبت
        ratio = 1.0
        if vol_sell > 0:
            ratio = round(vol_buy / vol_sell, 2)

        # ═══════════════════════════════════════════════════════
        # استراتژی جدید — بر اساس درس فولاد
        # ═══════════════════════════════════════════════════════

        score = 0
        reasons = []
        category = ""

        # ۱. صف خرید (40 امتیاز!) — مهم‌ترین
        if has_buy_queue:
            score += 40
            reasons.append("SAFE KHARID (40)")
            category = "QUEUE_BUY"
        elif has_sell_queue:
            return None  # صف فروش = نخر

        # ۲. حقوقی خریدار (25 امتیاز)
        if vol_sell_n > 0:
            ratio_n = vol_buy_n / vol_sell_n
            if ratio_n > 5:
                score += 25
                reasons.append(f"Hoqoqi={ratio_n:.1f}x (25)")
            elif ratio_n > 2:
                score += 20
                reasons.append(f"Hoqoqi={ratio_n:.1f}x (20)")
            elif ratio_n > 1:
                score += 10
                reasons.append(f"Hoqoqi={ratio_n:.1f}x (10)")
        elif vol_buy_n > 0:
            score += 15
            reasons.append("Hoqoqi faghat kharidar (15)")

        # ۳. P/E (15 امتیاز)
        if pe:
            if pe < 5:
                score += 15
                reasons.append(f"P/E={pe} (15)")
            elif pe < 8:
                score += 10
                reasons.append(f"P/E={pe} (10)")
            elif pe < 12:
                score += 5
                reasons.append(f"P/E={pe} (5)")

        # ۴. RSI (10 امتیاز)
        if rsi:
            if rsi < 30:
                score += 10
                reasons.append(f"RSI={rsi} (10)")
            elif rsi < 40:
                score += 7
                reasons.append(f"RSI={rsi} (7)")
            elif rsi < 50:
                score += 3
                reasons.append(f"RSI={rsi} (3)")

        # ۵. حقیقی خریدار (10 امتیاز)
        if vol_sell > 0:
            ratio_r = vol_buy / vol_sell
            if ratio_r > 1.5:
                score += 10
                reasons.append(f"Haghighi={ratio_r:.1f}x (10)")
            elif ratio_r > 1:
                score += 5
                reasons.append(f"Haghighi={ratio_r:.1f}x (5)")

        # ═══════════════════════════════════════════════════════

        return {
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "change": change,
            "pe": pe,
            "rsi": rsi,
            "ratio": ratio,
            "score": score,
            "category": category,
            "has_buy_queue": has_buy_queue,
            "has_sell_queue": has_sell_queue,
            "vol_buy_n": vol_buy_n,
            "vol_sell_n": vol_sell_n,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": round(min_a * 0.98) if min_a > 0 else 0,
            "profit": round((max_a / min_a - 1) * 100 - 1.25, 2) if min_a > 0 else 0,
            "reasons": reasons,
        }
    except Exception:
        return None


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🎯 استراتژی جدید — بر اساس درس فولاد")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    safe_print("  📌 درس‌ها:")
    safe_print("     1. صف خرید > RSI")
    safe_print("     2. تقاضا مهم‌تره")
    safe_print("     3. سهم‌های قوی (فولاد) مستقل")
    safe_print("     4. RSI بالا ≠ فروش")
    safe_print("")

    # دریافت داده
    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    # تحلیل
    safe_print("  🔍 تحلیل با استراتژی جدید...")
    safe_print("")

    results = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        if i % 500 == 0:
            safe_print(f"     {i}/{len(df)}...")

        r = analyze_stock_v2(row)
        if r and r["score"] >= 40:
            results.append(r)

    safe_print(f"  ✅ {len(results)} کاندید")
    safe_print("")

    # مرتب‌سازی
    results.sort(key=lambda x: -x["score"])
    top = results[:10]

    # نمایش
    safe_print("=" * 100)
    safe_print(f"  🏆 بهترین ۱۰ سهم (استراتژی جدید)")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  {'#':<3} | {'نماد':<12} | {'قیمت':>10} | {'P/E':>5} | {'RSI':>5} | {'نسبت':>6} | {'امتیاز':>6} | {'صف':>5}")
    safe_print("  " + "-" * 105)

    for i, s in enumerate(top, 1):
        queue = "BUY" if s["has_buy_queue"] else "---"
        safe_print(
            f"  {i:<3} | "
            f"{s['symbol'][:12]:<12} | "
            f"{int(s['last']):>10,} | "
            f"{s['pe'] if s['pe'] else 0:>5} | "
            f"{s['rsi'] if s['rsi'] else 0:>5} | "
            f"{s['ratio']:>6} | "
            f"{s['score']:>4}/100 | "
            f"{queue:>5}"
        )

    safe_print("")

    # جزئیات
    safe_print("=" * 100)
    safe_print(f"  📊 جزئیات ۵ سهم برتر")
    safe_print("=" * 100)
    safe_print("")

    for i, s in enumerate(top[:5], 1):
        safe_print(f"  ── {i}. {s['symbol']} ({s['name'][:30]}) ──")
        safe_print(f"     💰 قیمت:   {int(s['last']):,} ({s['change']:+.2f}%)")
        safe_print(f"     📈 P/E:    {s['pe']}")
        safe_print(f"     📉 RSI:    {s['rsi']}")
        safe_print(f"     📊 نسبت:   {s['ratio']}")
        safe_print(f"     🎯 امتیاز: {s['score']}/100")
        if s["has_buy_queue"]:
            safe_print(f"     🟢 صف خرید")
        safe_print("")
        safe_print(f"     💡 استراتژی:")
        safe_print(f"        🟢 خرید:    {int(s['buy_target']):,}")
        safe_print(f"        🔴 فروش:    {int(s['sell_target']):,}")
        safe_print(f"        ⛔ حدضرر:   {int(s['stop_loss']):,}")
        safe_print(f"        💰 سود:     {s['profit']:.2f}%")
        safe_print("")
        safe_print(f"     📊 دلایل:")
        for r in s['reasons']:
            safe_print(f"        ✅ {r}")
        safe_print("")

    # ذخیره
    output = PROJECT_ROOT / "reports" / f"strategy_v2_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "strategy": "v2 — queue priority",
            "top": top,
        }, f, ensure_ascii=False, indent=2)

    safe_print("=" * 100)
    safe_print(f"  💾 ذخیره: {output}")
    safe_print("=" * 100)
    safe_print("")


if __name__ == "__main__":
    main()
