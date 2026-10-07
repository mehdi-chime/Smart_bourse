# check_for_tomorrow.py
# بررسی کامل برای فردا — با AI
# اجرا: python check_for_tomorrow.py

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


def get_ai_advice(symbol, ratio, rsi, tech_score, last_price):
    try:
        from ai_integration import get_ai_advice as ai_adv
        return ai_adv(
            symbol=symbol,
            category="SAFE_BUY",
            ratio=ratio,
            rsi=rsi,
            technical_score=tech_score,
            last_price=last_price,
        )
    except Exception as e:
        return {
            "final_score": 50,
            "advice": f"AI error: {e}",
            "confidence": 0.5,
            "mode": "error",
        }


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


def analyze_stock(row):
    """تحلیل کامل یه سهم"""
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol:
            return None

        # قیمت‌ها
        last = float(row.get("Last") or row.get("Close") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0 or min_a <= 0 or max_a <= 0:
            return None

        # P/E
        pe = None
        if eps > 0:
            pe = round(last / eps, 2)
            if pe > 15 or pe < 0:
                return None

        # حجم
        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        total_vol = vol_buy + vol_sell
        if total_vol < 100_000:
            return None

        # صف
        bid_v1 = float(row.get("BidVolume1") or 0)
        ask_v1 = float(row.get("AskVolume1") or 0)
        has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
        has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

        if has_sell_queue:
            return None  # صف فروش = نخر

        # RSI + ATR
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

        if rsi is None or atr_pct is None:
            return None

        # فیلتر RSI (فقط پایین)
        if rsi > 60:
            return None

        # فیلتر ATR
        if atr_pct < 2.0:
            return None

        # نسبت
        ratio = 1.0
        if vol_sell > 0:
            ratio = round(vol_buy / vol_sell, 2)

        # AI
        ai_result = get_ai_advice(
            symbol=symbol,
            ratio=ratio,
            rsi=rsi,
            tech_score=50,
            last_price=last,
        )

        # امتیاز
        score = 0
        reasons = []

        # P/E (25)
        if pe:
            if pe < 5:
                score += 25
                reasons.append(f"P/E={pe} kheili khoob")
            elif pe < 8:
                score += 20
                reasons.append(f"P/E={pe} khoob")
            elif pe < 12:
                score += 15
                reasons.append(f"P/E={pe} monaseb")

        # RSI (25)
        if rsi < 25:
            score += 25
            reasons.append(f"RSI={rsi} kheili paeen")
        elif rsi < 35:
            score += 20
            reasons.append(f"RSI={rsi} paeen")
        elif rsi < 45:
            score += 12
            reasons.append(f"RSI={rsi} monaseb")

        # ATR (20)
        if atr_pct > 4:
            score += 20
            reasons.append(f"ATR={atr_pct}% bala")
        elif atr_pct > 3:
            score += 15
            reasons.append(f"ATR={atr_pct}% khob")

        # حقوقی (20)
        if vol_sell_n > 0:
            ratio_n = vol_buy_n / vol_sell_n
            if ratio_n > 3:
                score += 20
                reasons.append(f"Hoqoqi={ratio_n:.1f}x ghavi")
            elif ratio_n > 1.5:
                score += 15
                reasons.append(f"Hoqoqi={ratio_n:.1f}x")
            elif ratio_n > 1:
                score += 8
        elif vol_buy_n > 0:
            score += 15
            reasons.append("Hoqoqi faghat kharidar")

        # حقیقی (10)
        if vol_sell > 0:
            ratio_r = vol_buy / vol_sell
            if ratio_r > 1.5:
                score += 10
                reasons.append(f"Haghighi={ratio_r:.1f}x")

        # AI bonus
        ai_score = ai_result.get("final_score", 50)
        if ai_score > 60:
            score += 10
            reasons.append(f"AI={ai_score} khoob")
        elif ai_score > 50:
            score += 5

        # فاصله از کف
        distance_from_min = (last - min_a) / min_a * 100
        if distance_from_min > 10:
            return None

        # سود
        profit = (max_a / min_a - 1) * 100 - 1.25
        if profit < 3:
            return None

        return {
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "yesterday": yesterday,
            "min_a": min_a,
            "max_a": max_a,
            "change": change,
            "eps": eps,
            "pe": pe,
            "rsi": rsi,
            "atr_pct": atr_pct,
            "vol_buy": vol_buy,
            "vol_sell": vol_sell,
            "vol_buy_n": vol_buy_n,
            "vol_sell_n": vol_sell_n,
            "ratio": ratio,
            "score": score,
            "profit": profit,
            "distance_from_min": distance_from_min,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": round(min_a * 0.98),
            "ai_score": ai_score,
            "ai_advice": ai_result.get("advice", ""),
            "ai_confidence": ai_result.get("confidence", 0.5),
            "ai_mode": ai_result.get("mode", ""),
            "reasons": reasons,
        }
    except Exception:
        return None


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🎯 بررسی برای فردا")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    # دریافت داده
    safe_print("  📡 دریافت داده زنده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    # وضعیت بازار
    positive = 0
    negative = 0
    total = 0

    for _, row in df.iterrows():
        try:
            change = float(row.get("ChangePct") or 0)
            total += 1
            if change > 0:
                positive += 1
            elif change < 0:
                negative += 1
        except:
            continue

    market_pct = positive / total * 100 if total > 0 else 0

    safe_print(f"  📊 بازار: {market_pct:.1f}% مثبت")
    safe_print(f"     🟢 مثبت: {positive}")
    safe_print(f"     🔴 منفی: {negative}")
    safe_print("")

    # تحلیل
    safe_print("  🔍 تحلیل کامل...")
    safe_print("")

    results = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        if i % 500 == 0:
            safe_print(f"     {i}/{len(df)}...")

        r = analyze_stock(row)
        if r:
            results.append(r)

    safe_print(f"  ✅ {len(results)} کاندید")
    safe_print("")

    # مرتب‌سازی
    results.sort(key=lambda x: -x["score"])
    top = results[:10]

    # نمایش
    safe_print("=" * 100)
    safe_print(f"  🏆 بهترین ۱۰ سهم برای فردا")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  {'#':<3} | {'نماد':<12} | {'قیمت':>10} | {'P/E':>5} | {'RSI':>5} | {'AI':>5} | {'امتیاز':>6} | {'سود':>6}")
    safe_print("  " + "-" * 95)

    for i, s in enumerate(top, 1):
        safe_print(
            f"  {i:<3} | "
            f"{s['symbol'][:12]:<12} | "
            f"{int(s['last']):>10,} | "
            f"{s['pe'] if s['pe'] else 0:>5} | "
            f"{s['rsi']:>5} | "
            f"{s['ai_score']:>5} | "
            f"{s['score']:>4}/100 | "
            f"{s['profit']:>5.2f}%"
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
        safe_print(f"     📊 ATR:    {s['atr_pct']}%")
        safe_print(f"     📊 نسبت:   {s['ratio']}")
        safe_print(f"     🤖 AI:     {s['ai_score']} ({s['ai_advice']})")
        safe_print(f"     🎯 امتیاز: {s['score']}/100")
        safe_print("")
        safe_print(f"     💡 استراتژی:")
        safe_print(f"        🟢 خرید:    {int(s['buy_target']):,}")
        safe_print(f"        🔴 فروش:    {int(s['sell_target']):,}")
        safe_print(f"        ⛔ حدضرر:   {int(s['stop_loss']):,}")
        safe_print(f"        💰 سود:     {s['profit']:.2f}%")
        safe_print("")
        safe_print(f"     📊 دلایل:")
        for r in s['reasons'][:6]:
            safe_print(f"        ✅ {r}")
        safe_print("")

    # ذخیره
    output = PROJECT_ROOT / "reports" / f"check_for_tomorrow_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_pct": market_pct,
            "positive": positive,
            "negative": negative,
            "top": top,
            "all": results,
        }, f, ensure_ascii=False, indent=2)

    safe_print("=" * 100)
    safe_print(f"  💾 ذخیره: {output}")
    safe_print("=" * 100)
    safe_print("")

    # ارسال به ایتا
    safe_print("  📱 ارسال به ایتا...")

    msg = f"🎯 بررسی برای فردا\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg += f"📊 بازار: {market_pct:.1f}% مثبت\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, s in enumerate(top[:5], 1):
        msg += f"{i}. {s['symbol']}\n"
        msg += f"   💰 {int(s['last']):,}\n"
        msg += f"   📉 RSI: {s['rsi']}\n"
        if s['pe']:
            msg += f"   📈 P/E: {s['pe']}\n"
        msg += f"   🤖 AI: {s['ai_score']}\n"
        msg += f"   🎯 {s['score']}/100\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if send_eitaa(msg):
        safe_print("     ✅ ارسال شد")
    else:
        safe_print("     ❌ خطا")
    safe_print("")


if __name__ == "__main__":
    main()
