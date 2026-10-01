# smart_bourse_v10.py
# Smart_Bourse v10 - جامع و نهایی
# اجرا: python smart_bourse_v10.py

import os
import sys
import json
import time
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

# AI Integration
try:
    from ai_integration import get_ai_advice, record_ai_signal
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


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


def analyze_stock(symbol):
    """تحلیل کامل یه سهم"""
    result = {
        "symbol": symbol,
        "found": False,
        "error": None,
    }

    # ۱. داده زنده
    try:
        df = att.get_live_market()
        if df is None or df.empty:
            result["error"] = "Live data error"
            return result

        if "InstrumentType" in df.columns:
            df = df[df["InstrumentType"] == 300]

        found = None
        for _, row in df.iterrows():
            if normalize(str(row.get("Symbol", ""))) == normalize(symbol):
                found = row
                break

        if found is None:
            result["error"] = "Symbol not found"
            return result

        result["found"] = True
        result["name"] = str(found.get("Name", ""))

        # قیمت‌ها
        last = float(found.get("Last") or 0)
        yesterday = float(found.get("Yesterday") or 0)
        min_a = float(found.get("MinAllowed") or 0)
        max_a = float(found.get("MaxAllowed") or 0)
        change = float(found.get("ChangePct") or 0)
        eps = float(found.get("EPS") or 0)
        shares = float(found.get("SharesOutstanding") or 0)
        base_vol = float(found.get("BaseVolume") or 0)

        result["last"] = last
        result["yesterday"] = yesterday
        result["min_a"] = min_a
        result["max_a"] = max_a
        result["change"] = change
        result["eps"] = eps

        # P/E
        if eps > 0:
            pe = last / eps
            result["pe"] = round(pe, 2)
        else:
            pe = None
            result["pe"] = None

        # شناوری
        if shares > 0:
            free_float = base_vol if base_vol > 0 else shares * 0.3
            float_pct = (free_float / shares) * 100
            result["float_pct"] = round(float_pct, 1)
            result["free_float"] = free_float

        # سفارشات
        vol_buy = float(found.get("Vol_buy_retail") or 0)
        vol_sell = float(found.get("Vol_sell_retail") or 0)
        vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

        result["vol_buy"] = vol_buy
        result["vol_sell"] = vol_sell
        result["vol_buy_n"] = vol_buy_n
        result["vol_sell_n"] = vol_sell_n

        # صف
        bid_v1 = float(found.get("BidVolume1") or 0)
        ask_v1 = float(found.get("AskVolume1") or 0)
        result["has_buy_queue"] = (ask_v1 == 0 and bid_v1 > 0)
        result["has_sell_queue"] = (bid_v1 == 0 and ask_v1 > 0)
        result["bid_v1"] = bid_v1
        result["ask_v1"] = ask_v1

    except Exception as e:
        result["error"] = f"Live error: {e}"
        return result

    # ۲. تاریخچه
    try:
        hist = get_history_safe(symbol)
        if hist is None:
            result["error"] = "History not found"
            return result

        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        rsi = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)
        ma5 = calc_ma(closes, 5)
        ma20 = calc_ma(closes, 20)
        ma50 = calc_ma(closes, 50)

        result["rsi"] = rsi
        if atr_val and last > 0:
            result["atr_pct"] = round((atr_val / last * 100), 2)
        result["ma5"] = ma5
        result["ma20"] = ma20
        result["ma50"] = ma50

        # روند
        if ma5 and ma20 and ma50:
            if ma5 > ma20 > ma50:
                result["trend"] = "صعودی"
            elif ma5 < ma20 < ma50:
                result["trend"] = "نزولی"
            else:
                result["trend"] = "خنثی"
        else:
            result["trend"] = "نامشخص"

    except Exception as e:
        result["error"] = f"History error: {e}"
        return result

    # ۳. امتیازدهی و تصمیم
    score = 0
    max_score = 0
    reasons = []

    # RSI (30)
    max_score += 30
    rsi = result.get("rsi")
    if rsi:
        if rsi < 15:
            score += 30
            reasons.append(f"RSI={rsi} (اشباع فروش شدید)")
        elif rsi < 20:
            score += 25
            reasons.append(f"RSI={rsi} (اشباع فروش)")
        elif rsi < 30:
            score += 20
            reasons.append(f"RSI={rsi} (فروش)")
        elif rsi < 40:
            score += 12
            reasons.append(f"RSI={rsi} (نزدیک فروش)")
        elif rsi < 50:
            score += 5
        elif rsi > 70:
            score -= 10
            reasons.append(f"RSI={rsi} (اشباع خرید) ❌")

    # P/E (25)
    max_score += 25
    pe = result.get("pe")
    if pe and pe > 0:
        if pe < 3:
            score += 25
            reasons.append(f"P/E={pe} (فوق‌العاده ارزون)")
        elif pe < 5:
            score += 20
            reasons.append(f"P/E={pe} (خیلی ارزون)")
        elif pe < 8:
            score += 15
            reasons.append(f"P/E={pe} (ارزون)")
        elif pe < 12:
            score += 10
            reasons.append(f"P/E={pe} (متعادل)")
        elif pe < 15:
            score += 5
            reasons.append(f"P/E={pe} (قابل قبول)")
        else:
            reasons.append(f"P/E={pe} (گرون) ❌")
    elif pe and pe < 0:
        reasons.append("EPS منفی ❌")
    else:
        reasons.append("EPS نامشخص ❌")

    # حقوقی (20)
    max_score += 20
    vol_buy_n = result.get("vol_buy_n", 0)
    vol_sell_n = result.get("vol_sell_n", 0)
    if vol_sell_n > 0:
        ratio = vol_buy_n / vol_sell_n
        if ratio > 3:
            score += 20
            reasons.append(f"حقوقی خریدار ({ratio:.1f}x)")
        elif ratio > 1.5:
            score += 15
            reasons.append(f"حقوقی خریدار ({ratio:.1f}x)")
        elif ratio > 1:
            score += 8
        else:
            reasons.append(f"حقوقی فروشنده ({ratio:.2f}x) ❌")
    elif vol_buy_n > 0:
        score += 15
        reasons.append("حقوقی فقط خریدار")
    else:
        reasons.append("حقوقی نداره")

    # ATR (15)
    max_score += 15
    atr = result.get("atr_pct", 0)
    if atr > 4.5:
        score += 15
        reasons.append(f"ATR={atr}% (نوسان بالا)")
    elif atr > 4:
        score += 12
        reasons.append(f"ATR={atr}% (نوسان خوب)")
    elif atr > 3:
        score += 8
    elif atr > 2.5:
        score += 5
    else:
        reasons.append(f"ATR={atr}% (نوسان کم) ❌")

    # روند (10)
    max_score += 10
    trend = result.get("trend")
    if trend == "صعودی":
        score += 10
        reasons.append("روند صعودی")
    elif trend == "خنثی":
        score += 5
        reasons.append("روند خنثی")
    elif trend == "نزولی":
        reasons.append("روند نزولی ❌")

    result["score"] = score
    result["max_score"] = max_score
    result["reasons"] = reasons

    # ۴. تصمیم نهایی
    percent = (score / max_score * 100) if max_score > 0 else 0
    result["percent"] = round(percent, 1)

    if percent >= 70:
        decision = "🟢 بخر"
    elif percent >= 55:
        decision = "🟡 با احتیاط"
    elif percent >= 40:
        decision = "🟠 صبر کن"
    else:
        decision = "🔴 نخر"

    # چک صف فروش
    if result.get("has_sell_queue"):
        decision = "🔴 صف فروش - نخر"
        reasons.append("صف فروش")

    # چک صف خرید
    if result.get("has_buy_queue"):
        reasons.append("صف خرید - نمی‌تونی بخری")

    result["decision"] = decision

    
    # AI Analysis
    if AI_AVAILABLE:
        try:
            ai_result = get_ai_advice(
                symbol=r.get('symbol', ''),
                category='SAFE_BUY',
                ratio=1.0,
                rsi=r.get('rsi'),
                technical_score=r.get('percent', 50),
                last_price=r.get('last'),
            )
            safe_print("")
            safe_print(f"  🤖 AI Analysis:")
            safe_print(f"     Final Score: {ai_result.get('final_score')}")
            safe_print(f"     Advice: {ai_result.get('advice')}")
            safe_print(f"     Confidence: {ai_result.get('confidence')}")
            safe_print(f"     Mode: {ai_result.get('mode')}")
        except Exception as e:
            pass

    # ۵. قیمت‌های معاملاتی
    if min_a > 0 and max_a > 0:
        result["buy_target"] = min_a
        result["sell_target"] = max_a
        result["stop_loss"] = round(min_a * 0.98)
        result["profit"] = round((max_a / min_a - 1) * 100 - 1.25, 2)

    return result


def print_analysis(r):
    """چاپ تحلیل"""
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  📊 تحلیل: {r.get('symbol', '?')}")
    safe_print("=" * 80)
    safe_print("")

    if r.get("error"):
        safe_print(f"  ❌ {r['error']}")
        safe_print("")
        return

    if not r.get("found"):
        safe_print(f"  ❌ سهم پیدا نشد")
        safe_print("")
        return

    # نام
    safe_print(f"  📌 {r['symbol']} - {r.get('name', '')}")
    safe_print("")

    # قیمت
    safe_print(f"  💰 قیمت‌ها:")
    safe_print(f"     آخرین:     {int(r['last']):>12,}")
    safe_print(f"     دیروز:     {int(r['yesterday']):>12,}")
    safe_print(f"     تغییر:     {r['change']:>11.2f}%")
    safe_print(f"     کف:        {int(r['min_a']):>12,}")
    safe_print(f"     سقف:       {int(r['max_a']):>12,}")
    safe_print("")

    # بنیادی
    safe_print(f"  📈 بنیادی:")
    if r.get("pe"):
        safe_print(f"     P/E:       {r['pe']:>12}")
    else:
        safe_print(f"     P/E:       {'?':>12}")
    safe_print(f"     EPS:       {int(r.get('eps', 0)):>12,}")
    if r.get("float_pct"):
        safe_print(f"     شناوری:    {r['float_pct']:>11.1f}%")
    safe_print("")

    # تکنیکال
    safe_print(f"  📉 تکنیکال:")
    safe_print(f"     RSI:       {r.get('rsi', '?'):>12}")
    safe_print(f"     ATR:       {r.get('atr_pct', '?'):>11}%")
    safe_print(f"     روند:      {r.get('trend', '?'):>12}")
    safe_print("")

    # حقوقی
    safe_print(f"  🏛️ حقوقی/حقیقی:")
    safe_print(f"     حقوقی خرید:  {int(r.get('vol_buy_n', 0)):>12,}")
    safe_print(f"     حقوقی فروش:  {int(r.get('vol_sell_n', 0)):>12,}")
    safe_print(f"     حقیقی خرید:  {int(r.get('vol_buy', 0)):>12,}")
    safe_print(f"     حقیقی فروش:  {int(r.get('vol_sell', 0)):>12,}")
    safe_print("")

    # صف
    if r.get("has_buy_queue"):
        safe_print(f"  🟢 صف خرید")
    elif r.get("has_sell_queue"):
        safe_print(f"  🔴 صف فروش")
    safe_print("")

    # دلایل
    safe_print(f"  📊 دلایل:")
    for reason in r.get("reasons", []):
        safe_print(f"     ✅ {reason}")
    safe_print("")

    # امتیاز
    safe_print(f"  ⭐ امتیاز: {r['score']}/{r['max_score']} ({r['percent']}%)")
    safe_print("")

    # تصمیم
    safe_print("=" * 80)
    safe_print(f"  🎯 تصمیم: {r['decision']}")
    safe_print("=" * 80)
    safe_print("")

    # استراتژی
    if r.get("buy_target"):
        safe_print(f"  💡 استراتژی:")
        safe_print(f"     🟢 خرید:    {int(r['buy_target']):>12,}")
        safe_print(f"     🔴 فروش:    {int(r['sell_target']):>12,}")
        safe_print(f"     ⛔ حدضرر:   {int(r['stop_loss']):>12,}")
        safe_print(f"     💰 سود:     {r['profit']:>11.2f}%")
        safe_print("")

    # پیام ایتا
    safe_print("=" * 80)
    safe_print("  📱 پیام ایتا:")
    safe_print("=" * 80)
    safe_print("")

    msg = f"📊 تحلیل {r['symbol']}\n"
    msg += f"📌 {r.get('name', '')}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 قیمت: {int(r['last']):,} ({r['change']:+.2f}%)\n"
    msg += f"📉 RSI: {r.get('rsi', '?')}\n"
    msg += f"📈 P/E: {r.get('pe', '?')}\n"
    msg += f"📊 ATR: {r.get('atr_pct', '?')}%\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    if r.get("buy_target"):
        msg += f"🟢 خرید: {int(r['buy_target']):,}\n"
        msg += f"🔴 فروش: {int(r['sell_target']):,}\n"
        msg += f"⛔ حدضرر: {int(r['stop_loss']):,}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🎯 تصمیم: {r['decision']}\n"
    msg += f"⭐ امتیاز: {r['percent']}%\n"

    safe_print(msg)
    safe_print("")


def send_to_eitaa(r):
    """ارسال به ایتا"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
        import requests

        msg = f"📊 تحلیل {r['symbol']}\n"
        msg += f"📌 {r.get('name', '')}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"💰 قیمت: {int(r['last']):,} ({r['change']:+.2f}%)\n"
        msg += f"📉 RSI: {r.get('rsi', '?')}\n"
        msg += f"📈 P/E: {r.get('pe', '?')}\n"
        msg += f"📊 ATR: {r.get('atr_pct', '?')}%\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        if r.get("buy_target"):
            msg += f"🟢 خرید: {int(r['buy_target']):,}\n"
            msg += f"🔴 فروش: {int(r['sell_target']):,}\n"
            msg += f"⛔ حدضرر: {int(r['stop_loss']):,}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🎯 تصمیم: {r['decision']}\n"
        msg += f"⭐ امتیاز: {r['percent']}%\n"

        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": msg}
        response = requests.post(url, data=data, timeout=15)

        if response.status_code == 200:
            safe_print("  ✅ پیام ایتا ارسال شد")
            return True
        else:
            safe_print(f"  ❌ خطای ایتا: {response.status_code}")
            return False
    except Exception as e:
        safe_print(f"  ❌ خطا: {e}")
        return False


def menu_manual_analysis():
    """تحلیل دستی یه سهم"""
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 تحلیل یه سهم")
    safe_print("=" * 80)
    safe_print("")

    symbol = input("  اسم سهم: ").strip()
    if not symbol:
        return

    safe_print(f"  🔍 تحلیل {symbol}...")
    safe_print("")

    r = analyze_stock(symbol)
    print_analysis(r)

    # ارسال به ایتا؟
    send = input("  📱 ارسال به ایتا؟ (y/n): ").strip().lower()
    if send == "y":
        send_to_eitaa(r)


def menu_market_scan():
    """اسکن کل بازار"""
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 اسکن کل بازار")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  کدوم اسکنر؟")
    safe_print("  ۱. golden_scanner (P/E + RSI)")
    safe_print("  ۲. smart_scanner_v5 (کامل)")
    safe_print("  ۳. tomorrow_v5 (پیشنهاد فردا)")
    safe_print("")

    choice = input("  شماره: ").strip()

    if choice == "1":
        script = "golden_scanner.py"
    elif choice == "2":
        script = "smart_scanner_v5.py"
    elif choice == "3":
        script = "tomorrow_v5.py"
    else:
        return

    script_path = PROJECT_ROOT / script
    if not script_path.exists():
        safe_print(f"  ❌ {script} پیدا نشد")
        return

    safe_print(f"  🚀 اجرای {script}...")
    safe_print("")

    import subprocess
    subprocess.run([sys.executable, str(script_path)], cwd=str(PROJECT_ROOT))
    input("\n  Enter...")


def menu_portfolio():
    """پرتفوی"""
    safe_print("")
    safe_print("=" * 80)
    safe_print("  💼 پرتفوی")
    safe_print("=" * 80)
    safe_print("")

    # لیست سهم‌های تو
    portfolio = [
        "فولاد", "تابان", "احیا", "سمهریز",
        "رتاپ", "خگستر", "خپارس"
    ]

    safe_print(f"  📋 سهم‌های تو: {len(portfolio)}")
    safe_print("")

    for i, sym in enumerate(portfolio, 1):
        safe_print(f"  {i}. {sym}")

    safe_print("")
    safe_print("  تحلیل همه؟ (y/n): ", end="")
    choice = input().strip().lower()

    if choice == "y":
        for sym in portfolio:
            safe_print(f"\n  🔍 تحلیل {sym}...")
            r = analyze_stock(sym)
            print_analysis(r)


def main():
    while True:
        safe_print("")
        safe_print("=" * 80)
        safe_print(f"  🎯 Smart_Bourse v10")
        safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        safe_print("=" * 80)
        safe_print("")
        safe_print("  ۱. 🔍 تحلیل یه سهم خاص")
        safe_print("  ۲. 📊 اسکن کل بازار")
        safe_print("  ۳. 💼 تحلیل پرتفوی")
        safe_print("  ۴. 📱 ارسال تحلیل به ایتا")
        safe_print("  ۵. ❌ خروج")
        safe_print("")

        try:
            choice = input("  Shomare: ").strip()
        except KeyboardInterrupt:
            safe_print("\n  خروج...")
            break

        if choice == "1":
            menu_manual_analysis()
        elif choice == "2":
            menu_market_scan()
        elif choice == "3":
            menu_portfolio()
        elif choice == "4":
            safe_print("  → از گزینه ۱ استفاده کن")
            input("  Enter...")
        elif choice == "5":
            safe_print("  خروج...")
            break
        else:
            safe_print("  ❌ نامعتبر")


if __name__ == "__main__":
    main()
