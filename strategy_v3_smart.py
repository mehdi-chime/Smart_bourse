# strategy_v3_smart.py
# استراتژی ترکیبی هوشمند
# اجرا: python strategy_v3_smart.py

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


def analyze_stock_v3(row):
    """تحلیل با استراتژی ترکیبی"""
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol:
            return None

        # فیلتر حذف
        if symbol.endswith("3") or symbol.endswith("ح"):
            return None

        last = float(row.get("Last") or row.get("Close") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0 or min_a <= 0 or max_a <= 0:
            return None

        # صف
        bid_v1 = float(row.get("BidVolume1") or 0)
        ask_v1 = float(row.get("AskVolume1") or 0)
        has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
        has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

        # اگه صف فروش = رد
        if has_sell_queue:
            return None

        # اگه صف خرید = رد (نمی‌تونی بخری)
        if has_buy_queue:
            return None

        # سفارشات
        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        total_vol = vol_buy + vol_sell
        if total_vol < 100_000:
            return None

        # P/E
        pe = None
        if eps > 0:
            pe = round(last / eps, 2)
            if pe > 15 or pe < 0:
                return None

        # تاریخچه
        hist = get_history_safe(symbol)
        if hist is None:
            return None

        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        rsi = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)
        atr_pct = None

        if atr_val and last > 0:
            atr_pct = round((atr_val / last * 100), 2)

        ma5 = calc_ma(closes, 5)
        ma20 = calc_ma(closes, 20)
        ma50 = calc_ma(closes, 50)

        if rsi is None or atr_pct is None:
            return None

        # فیلتر RSI (فقط 20-50)
        if rsi > 50 or rsi < 20:
            return None

        # فیلتر ATR
        if atr_pct < 2.5:
            return None

        # فاصله از کف
        distance_from_min = (last - min_a) / min_a * 100
        if distance_from_min > 10:
            return None

        # سود
        profit = (max_a / min_a - 1) * 100 - 1.25
        if profit < 3:
            return None

        # نسبت
        ratio = 1.0
        if vol_sell > 0:
            ratio = round(vol_buy / vol_sell, 2)

        # ═══════════════════════════════════════════════════════
        # امتیازدهی
        # ═══════════════════════════════════════════════════════

        score = 0
        reasons = []

        # ۱. RSI (25)
        if rsi < 25:
            score += 25
            reasons.append(f"RSI={rsi} (25)")
        elif rsi < 35:
            score += 20
            reasons.append(f"RSI={rsi} (20)")
        elif rsi < 45:
            score += 10
            reasons.append(f"RSI={rsi} (10)")

        # ۲. P/E (20)
        if pe:
            if pe < 5:
                score += 20
                reasons.append(f"P/E={pe} (20)")
            elif pe < 8:
                score += 15
                reasons.append(f"P/E={pe} (15)")
            elif pe < 12:
                score += 10
                reasons.append(f"P/E={pe} (10)")

        # ۳. ATR (15)
        if atr_pct > 4:
            score += 15
            reasons.append(f"ATR={atr_pct}% (15)")
        elif atr_pct > 3:
            score += 10
            reasons.append(f"ATR={atr_pct}% (10)")

        # ۴. روند (15)
        if ma5 and ma20 and ma50:
            if ma5 > ma20 > ma50:
                score += 15
                reasons.append("Rوند صعودی (15)")
            elif ma5 > ma20:
                score += 10
                reasons.append("MA5 > MA20 (10)")

        # ۵. حقوقی (15)
        if vol_sell_n > 0:
            ratio_n = vol_buy_n / vol_sell_n
            if ratio_n > 3:
                score += 15
                reasons.append(f"Hoqoqi={ratio_n:.1f}x (15)")
            elif ratio_n > 1.5:
                score += 10
                reasons.append(f"Hoqoqi={ratio_n:.1f}x (10)")

        # ۶. حجم (10)
        if total_vol > 1_000_000:
            score += 10
            reasons.append(f"Volume (10)")
        elif total_vol > 500_000:
            score += 5
            reasons.append(f"Volume (5)")

        return {
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "min_a": min_a,
            "max_a": max_a,
            "change": change,
            "pe": pe,
            "rsi": rsi,
            "atr_pct": atr_pct,
            "ma5": ma5,
            "ma20": ma20,
            "ma50": ma50,
            "ratio": ratio,
            "total_vol": total_vol,
            "score": score,
            "profit": profit,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": round(min_a * 0.98),
            "reasons": reasons,
        }
    except Exception:
        return None


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🎯 استراتژی ترکیبی هوشمند v3")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    safe_print("  📌 فیلترها:")
    safe_print("     - RSI: 20-50 (پایین)")
    safe_print("     - P/E: < 15 (ارزون)")
    safe_print("     - ATR: > 2.5% (نوسان)")
    safe_print("     - MA: روند صعودی")
    safe_print("     - حقوقی: خریدار")
    safe_print("     - صف: نخر (بتونی بخری)")
    safe_print("")

    # دریافت
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
    safe_print("  🔍 تحلیل...")
    safe_print("")

    results = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        if i % 500 == 0:
            safe_print(f"     {i}/{len(df)}...")

        r = analyze_stock_v3(row)
        if r and r["score"] >= 40:
            results.append(r)

    safe_print(f"  ✅ {len(results)} کاندید")
    safe_print("")

    # مرتب‌سازی
    results.sort(key=lambda x: -x["score"])
    top = results[:10]

    # نمایش
    safe_print("=" * 100)
    safe_print(f"  🏆 بهترین ۱۰ سهم (استراتژی v3)")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  {'#':<3} | {'نماد':<12} | {'قیمت':>10} | {'P/E':>5} | {'RSI':>5} | {'ATR':>5} | {'امتیاز':>6} | {'سود':>6}")
    safe_print("  " + "-" * 100)

    for i, s in enumerate(top, 1):
        safe_print(
            f"  {i:<3} | "
            f"{s['symbol'][:12]:<12} | "
            f"{int(s['last']):>10,} | "
            f"{s['pe'] if s['pe'] else 0:>5} | "
            f"{s['rsi']:>5} | "
            f"{s['atr_pct']:>4.1f}% | "
            f"{s['score']:>4}/100 | "
            f"{s['profit']:>5.2f}%"
        )

    safe_print("")

    # جزئیات
    for i, s in enumerate(top[:5], 1):
        safe_print(f"  ── {i}. {s['symbol']} ({s['name'][:30]}) ──")
        safe_print(f"     💰 قیمت:   {int(s['last']):,} ({s['change']:+.2f}%)")
        safe_print(f"     📈 P/E:    {s['pe']}")
        safe_print(f"     📉 RSI:    {s['rsi']}")
        safe_print(f"     📊 ATR:    {s['atr_pct']}%")
        safe_print(f"     📊 MA5:    {int(s['ma5']) if s['ma5'] else '?':,}")
        safe_print(f"     📊 MA20:   {int(s['ma20']) if s['ma20'] else '?':,}")
        safe_print(f"     🎯 امتیاز: {s['score']}/100")
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
    output = PROJECT_ROOT / "reports" / f"strategy_v3_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "strategy": "v3 — smart combined",
            "top": top,
        }, f, ensure_ascii=False, indent=2)

    safe_print("=" * 100)
    safe_print(f"  💾 ذخیره: {output}")
    safe_print("=" * 100)


if __name__ == "__main__":
    main()
