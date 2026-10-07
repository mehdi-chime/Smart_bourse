# check_khepars.py
# بررسی کامل خپارس برای فروش
# اجرا: python check_khepars.py

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

# قیمت خرید تو (اگه می‌دونی)
BUY_PRICE = 0  # ← اگه می‌دونی بذار


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
    safe_print("  📊 بررسی کامل خپارس")
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

    # پیدا کردن خپارس
    found = None
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if normalize("خپارس") == normalize(symbol):
            found = row
            break

    if found is None:
        safe_print("  ❌ خپارس پیدا نشد!")
        return

    safe_print(f"     ✅ پیدا شد")

    # اطلاعات
    symbol = str(found.get("Symbol", ""))
    name = str(found.get("Name", ""))
    last = float(found.get("Last") or found.get("Close") or 0)
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

    # نسبت
    ratio = 1.0
    if vol_sell > 0:
        ratio = round(vol_buy / vol_sell, 2)

    # RSI + ATR
    hist = get_history_safe(symbol)
    rsi = None
    atr_pct = None
    ma5 = None
    ma20 = None
    ma50 = None

    if hist is not None:
        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        rsi = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)
        if atr_val and last > 0:
            atr_pct = round((atr_val / last * 100), 2)

        # MA
        if len(closes) >= 5:
            ma5 = float(np.mean(closes[-5:]))
        if len(closes) >= 20:
            ma20 = float(np.mean(closes[-20:]))
        if len(closes) >= 50:
            ma50 = float(np.mean(closes[-50:]))

    # روند
    trend = "نامشخص"
    if ma5 and ma20 and ma50:
        if ma5 > ma20 > ma50:
            trend = "صعودی"
        elif ma5 < ma20 < ma50:
            trend = "نزولی"
        else:
            trend = "خنثی"

    # AI
    try:
        from ai_integration import get_ai_advice
        ai_result = get_ai_advice(
            symbol=symbol,
            category="SAFE_BUY",
            ratio=ratio,
            rsi=rsi,
            technical_score=50,
            last_price=last,
        )
        ai_score = ai_result.get("final_score", 50)
        ai_advice = ai_result.get("advice", "")
        ai_mode = ai_result.get("mode", "")
    except:
        ai_score = 50
        ai_advice = "N/A"
        ai_mode = "N/A"

    # ═══════════════════════════════════════════════════════
    # نمایش
    # ═══════════════════════════════════════════════════════

    safe_print("")
    safe_print(f"  📌 {symbol} - {name}")
    safe_print("")

    safe_print("  💰 قیمت‌ها:")
    safe_print(f"     آخرین:      {int(last):>12,}")
    safe_print(f"     دیروز:      {int(yesterday):>12,}")
    safe_print(f"     تغییر:      {change:>11.2f}%")
    safe_print(f"     کف:         {int(min_a):>12,}")
    safe_print(f"     سقف:        {int(max_a):>12,}")
    safe_print("")

    safe_print("  📈 بنیادی:")
    if pe:
        safe_print(f"     P/E:        {pe:>12}")
    safe_print(f"     EPS:        {int(eps):>12,}")
    safe_print("")

    safe_print("  📉 تکنیکال:")
    safe_print(f"     RSI:        {rsi if rsi else '?':>12}")
    safe_print(f"     ATR:        {atr_pct if atr_pct else '?':>11}%")
    safe_print(f"     MA5:        {int(ma5) if ma5 else '?':>12,}")
    safe_print(f"     MA20:       {int(ma20) if ma20 else '?':>12,}")
    safe_print(f"     MA50:       {int(ma50) if ma50 else '?':>12,}")
    safe_print(f"     روند:       {trend:>12}")
    safe_print("")

    safe_print("  🏛️ سفارشات:")
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

    safe_print("  🤖 AI:")
    safe_print(f"     Score:       {ai_score:>12}")
    safe_print(f"     Advice:      {ai_advice:>12}")
    safe_print(f"     Mode:        {ai_mode:>12}")
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # تصمیم
    # ═══════════════════════════════════════════════════════

    safe_print("=" * 100)
    safe_print("  🎯 تصمیم:")
    safe_print("=" * 100)
    safe_print("")

    decision = "🟡 نگه دار"
    reasons = []

    # چک صف فروش
    if has_sell_queue:
        decision = "🔴 بفروش (صف فروش!)"
        reasons.append("صف فروش")
    # چک RSI
    elif rsi and rsi > 75:
        decision = "🔴 بفروش (RSI اشباع)"
        reasons.append(f"RSI={rsi} اشباع")
    elif rsi and rsi < 30:
        decision = "🟢 نگه دار (فرصت)"
        reasons.append(f"RSI={rsi} اشباع فروش")
    # چک روند
    elif trend == "نزولی":
        decision = "🟠 مراقب (روند نزولی)"
        reasons.append("MA5 < MA20 < MA50")
    elif trend == "صعودی":
        reasons.append("MA5 > MA20 > MA50")
    # چک حقوقی
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

    # استراتژی
    safe_print(f"  💡 استراتژی:")
    if min_a > 0 and max_a > 0:
        safe_print(f"     🟢 خرید:    {int(min_a):>12,}")
        safe_print(f"     🔴 فروش:    {int(max_a):>12,}")
        safe_print(f"     ⛔ حدضرر:   {int(min_a * 0.98):>12,}")
        profit = (max_a / min_a - 1) * 100 - 1.25
        safe_print(f"     💰 سود:     {profit:>11.2f}%")
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # نکات مهم
    # ═══════════════════════════════════════════════════════

    safe_print("=" * 100)
    safe_print("  📌 نکات مهم:")
    safe_print("=" * 100)
    safe_print("")

    # چک منفی چند روز
    if hist is not None and len(hist) >= 5:
        closes = hist["Close"].tolist()
        recent = closes[-5:]

        # چند روز منفی
        negative_days = 0
        for i in range(1, len(recent)):
            if recent[i] < recent[i-1]:
                negative_days += 1

        safe_print(f"  📊 ۵ روز اخیر:")
        safe_print(f"     منفی: {negative_days} روز")
        safe_print(f"     از: {int(recent[0]):,}")
        safe_print(f"     به: {int(recent[-1]):,}")
        change_5d = (recent[-1] - recent[0]) / recent[0] * 100
        safe_print(f"     تغییر: {change_5d:+.2f}%")
        safe_print("")

        if negative_days >= 3:
            safe_print("  ⚠️ هشدار: ۳+ روز منفی متوالی!")
            safe_print("     احتمالاً روند نزولی")

    # ذخیره
    output = PROJECT_ROOT / "reports" / f"khepars_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "last": last,
        "change": change,
        "pe": pe,
        "rsi": rsi,
        "atr_pct": atr_pct,
        "trend": trend,
        "ai_score": ai_score,
        "decision": decision,
        "reasons": reasons,
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    safe_print(f"  💾 ذخیره: {output}")
    safe_print("")

    # ارسال به ایتا
    safe_print("  📱 ارسال به ایتا...")

    msg = f"📊 بررسی خپارس\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg += f"💰 {int(last):,} ({change:+.2f}%)\n"
    if rsi:
        msg += f"📉 RSI: {rsi}\n"
    if pe:
        msg += f"📈 P/E: {pe}\n"
    msg += f"📊 روند: {trend}\n"
    msg += f"🎯 {decision}\n"

    if send_eitaa(msg):
        safe_print("     ✅ ارسال شد")
    else:
        safe_print("     ❌ خطا")
    safe_print("")


if __name__ == "__main__":
    main()
