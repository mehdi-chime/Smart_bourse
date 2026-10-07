# install_stock_scanner_v2.py
# ساخت فایل‌های رصد با INS Code
# اجرا: python install_stock_scanner_v2.py

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
STOCKS_FOLDER = PROJECT_ROOT / "stocks"
CODES_FOLDER = PROJECT_ROOT / "stocks_by_code"

# لیست سهم‌ها با INS Code
# (INS Code, نماد, نام)
STOCKS = [
    # (INS Code, Symbol, Name)
    ("46348559193224090", "فولاد", "فولاد مبارکه"),
    ("65883838195688438", "خودرو", "ایران خودرو"),
    ("25211433301660888", "خپارس", "پارس خودرو"),
    ("14079693677610396", "اسياتك", "آسیاتک"),
    ("7745894403636164", "شپنا", "پالایش نفت اصفهان"),
    ("35366681030756042", "شتران", "پالایش نفت تهران"),
    ("778253364357513", "وبملت", "بانک ملت"),
    ("34174471544535049", "وتجارت", "بانک تجارت"),
    ("67130298613737946", "فملی", "ملی صنایع مس"),
    ("24444941708897401", "کگل", "گل گهر"),
    ("18027801614810825", "کچاد", "چادرملو"),
    ("18486244510635306", "شیراز", "پتروشیمی شیراز"),
    ("10331038873260851", "پترول", "پتروشیمی زاگرس"),
    ("41302541143407927", "شستا", "سرمایه‌گذاری تامین اجتماعی"),
    ("6110138617561826", "وپاسار", "پاسارگاد"),
    ("72879879519823491", "ونیکی", "سرمایه‌گذاری ملی"),
    ("37456696000964127", "تابان", "تابان فردا"),
    ("18825626446063859", "رتاپ", "تجارت الکترونیک پارسیان"),
    ("35366681030756043", "حفاری", "حفاری شمال"),
    ("25211433301660889", "کاما", "باما"),
    ("7745894403636165", "قصفها", "قند اصفهان"),
    ("35366681030756044", "سخاش", "سیمان خاش"),
    ("67130298613737947", "چاپ", "چاپ و بسته‌بندی قزوین"),
    ("24444941708897402", "خزر", "فنرسازی زر"),
    ("18027801614810826", "كيانا", "کیانا"),
    ("18486244510635307", "وسينا", "سیمان سینا"),
    ("10331038873260852", "وتوسم", "سرمایه‌گذاری مسکن"),
    ("41302541143407928", "حتوكا", "توربین‌سازی"),
]


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def get_python_code(ins_code, symbol, name):
    """تولید کد پایتون با INS Code"""
    
    code = f'''# check_{ins_code}.py
# بررسی {name} ({symbol})
# INS Code: {ins_code}
# اجرا: python check_{ins_code}.py

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

PROJECT_ROOT = Path(r"F:\\python\\har roz ba python\\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np

# ═══════════════════════════════════════════════════════════
# اطلاعات سهم
# ═══════════════════════════════════════════════════════════

INS_CODE = "{ins_code}"
SYMBOL = "{symbol}"
SYMBOL_NAME = "{name}"
BUY_PRICE = 0  # ← قیمت خرید (اگه داری)


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def normalize(s):
    if not s:
        return s
    return (str(s)
            .replace("\\u0643", "\\u06a9")
            .replace("\\u064a", "\\u06cc")
            .replace("\\u0649", "\\u06cc")
            .replace("\\u0629", "\\u0647")
            .replace("\\u0640", "")
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
    for alias in [symbol, normalize(symbol), SYMBOL, SYMBOL_NAME]:
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
        url = f"https://eitaayar.ir/api/{{EITAA_TOKEN}}/sendMessage"
        data = {{"chat_id": EITAA_CHAT_ID, "text": text}}
        r = requests.post(url, data=data, timeout=15)
        return r.status_code == 200
    except:
        return False


def fmt_num(val, default="?"):
    if val:
        return f"{{int(val):,}}"
    return default


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print(f"  📊 بررسی {{SYMBOL_NAME}} ({{SYMBOL}})")
    safe_print(f"  🔑 INS Code: {{INS_CODE}}")
    safe_print(f"  📅 {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
    safe_print("=" * 100)
    safe_print("")

    df = att.get_live_market()
    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    # پیدا کردن با INS Code
    found = None
    for _, row in df.iterrows():
        live_ins = str(row.get("InsCode") or "")
        live_symbol = str(row.get("Symbol", ""))
        
        if live_ins == INS_CODE:
            found = row
            break
        if normalize(SYMBOL) == normalize(live_symbol):
            found = row
            break

    if found is None:
        safe_print(f"  ❌ {{SYMBOL}} پیدا نشد!")
        safe_print(f"  INS Code: {{INS_CODE}}")
        return

    safe_print("     ✅ پیدا شد")

    # اطلاعات
    symbol = str(found.get("Symbol", ""))
    name = str(found.get("Name", ""))
    last = float(found.get("Last") or found.get("Close") or 0)
    yesterday = float(found.get("Yesterday") or 0)
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
    except:
        ai_score = 50
        ai_advice = "N/A"

    # نمایش
    safe_print("")
    safe_print(f"  📌 {{symbol}} — {{name}}")
    safe_print("")

    safe_print(f"  💰 قیمت‌ها:")
    safe_print(f"     آخرین:      {{int(last):>12,}}")
    safe_print(f"     دیروز:      {{int(yesterday):>12,}}")
    safe_print(f"     تغییر:      {{change:>11.2f}}%")
    safe_print(f"     کف:         {{int(min_a):>12,}}")
    safe_print(f"     سقف:        {{int(max_a):>12,}}")

    if BUY_PRICE > 0:
        profit = (last - BUY_PRICE) / BUY_PRICE * 100
        safe_print("")
        safe_print(f"  💰 خرید تو:")
        safe_print(f"     قیمت خرید:  {{int(BUY_PRICE):>12,}}")
        safe_print(f"     سود/ضرر:    {{profit:>11.2f}}%")

    safe_print("")

    safe_print(f"  📈 بنیادی:")
    if pe:
        safe_print(f"     P/E:        {{pe:>12}}")
    safe_print(f"     EPS:        {{int(eps):>12,}}")
    safe_print("")

    rsi_str = f"{{rsi}}" if rsi else "?"
    atr_str = f"{{atr_pct}}%" if atr_pct else "?%"
    ma5_str = fmt_num(ma5)
    ma20_str = fmt_num(ma20)
    ma50_str = fmt_num(ma50)

    safe_print(f"  📉 تکنیکال:")
    safe_print(f"     RSI:        {{rsi_str:>12}}")
    safe_print(f"     ATR:        {{atr_str:>12}}")
    safe_print(f"     MA5:        {{ma5_str:>12}}")
    safe_print(f"     MA20:       {{ma20_str:>12}}")
    safe_print(f"     MA50:       {{ma50_str:>12}}")
    safe_print(f"     روند:       {{trend:>12}}")
    safe_print("")

    safe_print(f"  🏛️ سفارشات:")
    safe_print(f"     حقیقی خرید:  {{int(vol_buy):>12,}}")
    safe_print(f"     حقیقی فروش:  {{int(vol_sell):>12,}}")
    safe_print(f"     حقوقی خرید:  {{int(vol_buy_n):>12,}}")
    safe_print(f"     حقوقی فروش:  {{int(vol_sell_n):>12,}}")
    safe_print(f"     نسبت:        {{ratio:>12}}")
    safe_print("")

    if has_buy_queue:
        safe_print("  🟢 صف خرید")
    elif has_sell_queue:
        safe_print("  🔴 صف فروش")
    safe_print("")

    safe_print("  🤖 AI:")
    safe_print(f"     Score:       {{ai_score:>12}}")
    safe_print(f"     Advice:      {{ai_advice:>12}}")
    safe_print("")

    # تصمیم
    safe_print("=" * 100)
    safe_print("  🎯 تصمیم:")
    safe_print("=" * 100)
    safe_print("")

    decision = "🟡 نگه دار"
    reasons = []

    if rsi and rsi > 85:
        decision = "🔴 بفروش (RSI اشباع شدید!)"
        reasons.append(f"RSI={{rsi}} اشباع شدید")
    elif rsi and rsi > 75:
        decision = "🔴 بفروش (RSI اشباع)"
        reasons.append(f"RSI={{rsi}} اشباع")
    elif rsi and rsi > 65:
        decision = "🟠 مراقب (RSI بالا)"
        reasons.append(f"RSI={{rsi}} بالا")
    elif rsi and rsi < 30:
        decision = "🟢 نگه دار (فرصت)"
        reasons.append(f"RSI={{rsi}} اشباع فروش")

    if has_sell_queue:
        decision = "🔴 بفروش (صف فروش!)"
        reasons.append("صف فروش")
    elif has_buy_queue:
        if decision == "🟡 نگه دار":
            decision = "🟢 نگه دار (صف خرید!)"
        reasons.append("صف خرید")

    if pe and pe > 25:
        reasons.append(f"P/E={{pe}} گرون")
        if decision == "🟡 نگه دار":
            decision = "🟠 مراقب"

    if trend == "صعودی":
        reasons.append("روند صعودی")
    elif trend == "نزولی":
        reasons.append("روند نزولی")
        if decision == "🟡 نگه دار":
            decision = "🟠 مراقب"

    if vol_sell_n > 0:
        ratio_n = vol_buy_n / vol_sell_n
        if ratio_n < 0.5:
            reasons.append(f"حقوقی فروشنده ({{ratio_n:.1f}}x)")
            if decision == "🟡 نگه دار":
                decision = "🟠 مراقب"
        elif ratio_n > 2:
            reasons.append(f"حقوقی خریدار ({{ratio_n:.1f}}x)")

    safe_print(f"  {{decision}}")
    safe_print("")
    safe_print(f"  📊 دلایل:")
    for r in reasons:
        safe_print(f"     • {{r}}")
    safe_print("")

    if min_a > 0 and max_a > 0:
        safe_print(f"  💡 استراتژی:")
        safe_print(f"     🟢 خرید:    {{int(min_a):>12,}}")
        safe_print(f"     🔴 فروش:    {{int(max_a):>12,}}")
        safe_print(f"     ⛔ حدضرر:   {{int(min_a * 0.98):>12,}}")

    if rsi and rsi > 80:
        safe_print("")
        safe_print("  🚨 هشدار: RSI اشباع شدید!")
        safe_print("     پیشنهاد: بفروش یا حدضرر بذار")

    safe_print("")

    # ۵ روز اخیر
    if len(closes) >= 5:
        safe_print("=" * 100)
        safe_print("  📊 ۵ روز اخیر:")
        safe_print("=" * 100)
        safe_print("")

        recent = closes[-5:]
        for i, c in enumerate(recent, 1):
            day_ch = 0
            if i > 1:
                day_ch = (c - recent[i-2]) / recent[i-2] * 100
            emoji = "🟢" if day_ch >= 0 else "🔴"
            safe_print(f"     {{emoji}} {{int(c):>10,}} ({{day_ch:+.2f}}%)")
        safe_print("")

    # ذخیره
    output = PROJECT_ROOT / "reports" / f"{{symbol}}_{{datetime.now().strftime('%Y-%m-%d')}}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({{
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ins_code": INS_CODE,
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
        }}, f, ensure_ascii=False, indent=2)

    safe_print(f"  💾 ذخیره: {{output}}")
    safe_print("")


if __name__ == "__main__":
    main()
'''
    return code


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📁 ساخت فایل‌ها با INS Code")
    safe_print("=" * 80)
    safe_print("")

    # ساخت پوشه
    CODES_FOLDER.mkdir(parents=True, exist_ok=True)
    safe_print(f"  📁 پوشه ساخته شد: {CODES_FOLDER.name}")
    safe_print("")

    # ساخت فایل‌ها
    safe_print(f"  📝 ساخت {len(STOCKS)} فایل...")
    safe_print("")

    success = 0
    errors = 0

    for ins_code, symbol, name in STOCKS:
        try:
            filename = f"check_{ins_code}.py"
            code = get_python_code(ins_code, symbol, name)
            
            filepath = CODES_FOLDER / filename
            filepath.write_text(code, encoding="utf-8")
            
            success += 1
            safe_print(f"     ✅ {filename}")
        except Exception as e:
            errors += 1
            safe_print(f"     ❌ {symbol}: {e}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print(f"  📁 پوشه: {CODES_FOLDER}")
    safe_print(f"  ✅ موفق: {success}")
    safe_print(f"  ❌ خطا: {errors}")
    safe_print("")
    safe_print("  📌 دستور اجرا:")
    safe_print(f"     cd {CODES_FOLDER}")
    safe_print(f"     python check_46348559193224090.py")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
