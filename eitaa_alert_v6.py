# eitaa_alert_v6.py
# هشدار کامل ایتا - v6
# اجرا: python eitaa_alert_v6.py

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
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np
import requests

# ═══════════════════════════════════════════════════════════
# تنظیمات
# ═══════════════════════════════════════════════════════════
MAX_PE = 15
MAX_RSI = 40
MIN_ATR = 2.5
MIN_VOLUME = 500_000
MIN_PROFIT = 3.5
TOP_N = 5

# Eitaa
sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
from alert_config import EITAA_TOKEN, EITAA_CHAT_ID


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
    try:
        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=20)
        return r.status_code == 200
    except Exception as e:
        safe_print(f"  ERR Eita: {e}")
        return False


def analyze_full(row):
    """تحلیل کامل"""
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            return None

        last = float(row.get("Last") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)
        shares = float(row.get("SharesOutstanding") or 0)
        base_vol = float(row.get("BaseVolume") or 0)

        if last <= 0 or min_a <= 0 or max_a <= 0:
            return None

        # P/E
        if eps <= 0:
            return None
        pe = last / eps
        if pe > MAX_PE or pe < 0:
            return None

        # شناوری
        free_float = 0
        float_pct = 0
        if shares > 0:
            free_float = base_vol if base_vol > 0 else shares * 0.3
            float_pct = (free_float / shares) * 100

        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        total_vol = vol_buy + vol_sell
        if total_vol < MIN_VOLUME:
            return None

        # صف فروش
        bid_v1 = float(row.get("BidVolume1") or 0)
        ask_v1 = float(row.get("AskVolume1") or 0)
        has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

        hist = get_history_safe(symbol)
        if hist is None:
            return None

        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        rsi = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)

        if rsi is None or atr_val is None:
            return None

        atr_pct = (atr_val / last * 100) if last > 0 else 0

        if rsi > MAX_RSI:
            return None
        if atr_pct < MIN_ATR:
            return None

        profit = (max_a / min_a - 1) * 100 - 1.25
        if profit < MIN_PROFIT:
            return None

        distance_from_min = (last - min_a) / min_a * 100
        if distance_from_min > 10:
            return None

        # امتیازدهی
        score = 0

        # P/E (25)
        if pe < 3:
            score += 25
        elif pe < 5:
            score += 20
        elif pe < 8:
            score += 15
        elif pe < 12:
            score += 10
        elif pe < 15:
            score += 5

        # RSI (25)
        if rsi < 15:
            score += 25
        elif rsi < 20:
            score += 20
        elif rsi < 25:
            score += 15
        elif rsi < 30:
            score += 10
        elif rsi < 40:
            score += 5

        # حقوقی (20)
        if vol_sell_n > 0:
            ratio = vol_buy_n / vol_sell_n
            if ratio > 3:
                score += 20
            elif ratio > 1.5:
                score += 15
            elif ratio > 1:
                score += 8
        elif vol_buy_n > 0:
            score += 15

        # ATR (15)
        if atr_pct > 4.5:
            score += 15
        elif atr_pct > 4:
            score += 12
        elif atr_pct > 3:
            score += 8
        elif atr_pct > 2.5:
            score += 5

        # شناوری (10)
        if float_pct > 50:
            score += 10
        elif float_pct > 30:
            score += 7
        elif float_pct > 20:
            score += 5

        # فاصله از کف (5)
        if distance_from_min < 1:
            score += 5
        elif distance_from_min < 2:
            score += 3

        # تحلیل حقوقی
        inst_status = "خنثی"
        if vol_sell_n > 0:
            ratio = vol_buy_n / vol_sell_n
            if ratio > 3:
                inst_status = f"خریدار قوی ({ratio:.1f}x)"
            elif ratio > 1.5:
                inst_status = f"خریدار ({ratio:.1f}x)"
            elif ratio > 1:
                inst_status = f"کم‌خریدار ({ratio:.1f}x)"
            else:
                inst_status = f"فروشنده ({ratio:.2f}x)"
        elif vol_buy_n > 0:
            inst_status = "فقط خریدار"

        # تحلیل RSI
        if rsi < 15:
            rsi_status = "اشباع فروش شدید"
        elif rsi < 20:
            rsi_status = "اشباع فروش"
        elif rsi < 30:
            rsi_status = "فروش"
        elif rsi < 40:
            rsi_status = "نزدیک فروش"
        else:
            rsi_status = "متوسط"

        # تحلیل P/E
        if pe < 5:
            pe_status = "خیلی ارزون"
        elif pe < 10:
            pe_status = "ارزون"
        elif pe < 15:
            pe_status = "متعادل"
        else:
            pe_status = "گرون"

        return {
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "yesterday": yesterday,
            "min_a": min_a,
            "max_a": max_a,
            "change": change,
            "eps": eps,
            "pe": round(pe, 2),
            "pe_status": pe_status,
            "rsi": rsi,
            "rsi_status": rsi_status,
            "atr_pct": round(atr_pct, 2),
            "free_float": free_float,
            "float_pct": round(float_pct, 1),
            "vol_buy": vol_buy,
            "vol_sell": vol_sell,
            "vol_buy_n": vol_buy_n,
            "vol_sell_n": vol_sell_n,
            "inst_status": inst_status,
            "has_sell_queue": has_sell_queue,
            "score": score,
            "profit": profit,
            "distance_from_min": distance_from_min,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": round(min_a * 0.98),
        }
    except Exception as e:
        return None


def format_number(n):
    """فرمت اعداد بزرگ"""
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.0f}M"
    elif n >= 1_000:
        return f"{n/1_000:.0f}K"
    return f"{n:.0f}"


def build_full_message(signals, market_pct, positive, negative):
    """پیام کامل ایتا"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    msg = f"🎯 Smart_Bourse v6\n"
    msg += f"📅 {date_str} | ⏰ {time_str}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 بازار: {market_pct:.1f}% مثبت\n"
    msg += f"🟢 {positive} | 🔴 {negative}\n"
    msg += f"🎯 فیلتر: P/E < 15 | RSI < 40\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if not signals:
        msg += "⏳ سیگنال جدیدی نیست\n"
        msg += "💡 بازار متعادل یا سبز\n"
        return msg

    msg += f"🏆 {len(signals)} سهم پیشنهادی:\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, s in enumerate(signals, 1):
        # هدر سهم
        msg += f"━━━ {i}️⃣ {s['symbol']} ━━━\n"
        msg += f"📌 {s['name'][:30]}\n"
        msg += "──────────────────────\n"

        # قیمت
        msg += f"💰 قیمت فعلی: {int(s['last']):,} ({s['change']:+.2f}%)\n"
        msg += f"📊 دیروز: {int(s['yesterday']):,}\n"
        msg += "──────────────────────\n"

        # بنیادی
        msg += f"📈 P/E: {s['pe']} ({s['pe_status']})\n"
        msg += f"📊 EPS: {int(s['eps']):,}\n"
        msg += f"💼 شناوری: {s['float_pct']:.0f}% ({format_number(s['free_float'])})\n"
        msg += "──────────────────────\n"

        # تکنیکال
        msg += f"📉 RSI: {s['rsi']} ({s['rsi_status']})\n"
        msg += f"📊 ATR: {s['atr_pct']:.2f}%\n"
        msg += "──────────────────────\n"

        # حقوقی
        msg += f"🏛️ حقوقی: {s['inst_status']}\n"
        msg += f"   خرید: {format_number(s['vol_buy_n'])}\n"
        msg += f"   فروش: {format_number(s['vol_sell_n'])}\n"
        msg += "──────────────────────\n"

        # صف
        if s['has_sell_queue']:
            msg += "🔴 صف فروش (دام؟)\n"
        msg += "──────────────────────\n"

        # استراتژی
        msg += f"🟢 خرید: {int(s['buy_target']):,}\n"
        msg += f"🔴 فروش: {int(s['sell_target']):,}\n"
        msg += f"⛔ حدضرر: {int(s['stop_loss']):,}\n"
        msg += f"💰 سود: {s['profit']:.2f}%\n"
        msg += "──────────────────────\n"

        # امتیاز
        msg += f"⭐ امتیاز: {s['score']}/100\n"
        msg += "\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 استراتژی:\n"
    msg += "   ۱. خرید روی کف (MinAllowed)\n"
    msg += "   ۲. فروش روی سقف (MaxAllowed)\n"
    msg += "   ۳. حد ضرر -2%\n"
    msg += "   ۴. ۳-۵ سهم، نه بیشتر\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🐜🐜 هر روز بهتر\n"

    return msg


def main():
    safe_print("")
    safe_print("=" * 110)
    safe_print(f"  Eitaa Alert v6 - کامل")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 110)
    safe_print("")

    safe_print("  Daryaft dade...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ERR")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    safe_print(f"  OK: {len(df)} sahm")
    safe_print("")

    # بازار
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
    safe_print(f"  Bazar: {market_pct:.1f}% mosbat ({positive}G/{negative}R)")
    safe_print("")

    safe_print("  Tahlil kamel (P/E + RSI + ATR + Hoqoqi + Shenavari)...")
    safe_print("")

    results = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        if i % 50 == 0:
            safe_print(f"     {i}/{len(df)}...")

        r = analyze_full(row)
        if r:
            results.append(r)

    safe_print(f"  OK: {len(results)} candidate")
    safe_print("")

    results.sort(key=lambda x: -x["score"])
    top = results[:TOP_N]

    # نمایش
    safe_print("=" * 110)
    safe_print(f"  Behtarin {len(top)} sahm")
    safe_print("=" * 110)
    safe_print("")

    for i, s in enumerate(top, 1):
        safe_print(f"  {i}. {s['symbol']} - {s['name'][:30]}")
        safe_print(f"     P/E: {s['pe']} | RSI: {s['rsi']} | ATR: {s['atr_pct']}%")
        safe_print(f"     حقوقی: {s['inst_status']}")
        safe_print(f"     امتیاز: {s['score']}/100 | سود: {s['profit']:.2f}%")
        safe_print("")

    # ارسال
    if top:
        msg = build_full_message(top, market_pct, positive, negative)
        if send_eitaa(msg):
            safe_print("  ✅ Eitaa ersal shod!")
        else:
            safe_print("  ❌ Eitaa ERR")

    # ذخیره
    output = PROJECT_ROOT / "data" / "hunter" / f"eitaa_v6_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "market_pct": market_pct,
            "top": top,
        }, f, ensure_ascii=False, indent=2)

    safe_print(f"  Save: {output}")
    safe_print("")
    safe_print("=" * 110)
    safe_print("")


if __name__ == "__main__":
    main()
