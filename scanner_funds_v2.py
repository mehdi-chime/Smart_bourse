# scanner_funds_v2.py
# اسکنر صندوق‌ها — نسخه ۲ (فقط صندوق واقعی)
# اجرا: python scanner_funds_v2.py

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


def is_fund(symbol, name):
    """چک کن صندوقه یا نه"""
    name_lower = str(name).lower()
    symbol_lower = str(symbol).lower()

    # ۱. حذف حق تقدم
    if symbol.endswith("3") or symbol.endswith("ح"):
        return False

    # ۲. نشانه‌های صندوق
    fund_keywords = [
        "صندوق", "ص.", "س.", "اهرمی", "اهرمي",
        "درآمد ثابت", "درامد ثابت", "سهامی", "سهامي",
        "شاخص", "شاخصی", "کالا", "طلا", "نقره",
        "مختلط", "تركيبي", "ترکیبی", "بخشی",
        "س.س", "س.ا", "س.ط", "س.ک",
    ]

    for kw in fund_keywords:
        if kw in name_lower or kw in symbol_lower:
            # اگه سهم (با EPS مثبت) بود، صندوق نیست
            return True

    return False


def detect_fund_type(name, symbol):
    """تشخیص نوع صندوق"""
    name_lower = str(name).lower()

    if any(k in name_lower for k in ["اهرمی", "اهرمي", "lever"]):
        return "اهرمی"
    if any(k in name_lower for k in ["درآمد", "درامد", "ثابت"]):
        return "درآمد ثابت"
    if any(k in name_lower for k in ["سهامی", "سهامي"]):
        return "سهامی"
    if any(k in name_lower for k in ["طلا", "نقره", "کالا"]):
        return "کالایی"
    if any(k in name_lower for k in ["شاخص", "index"]):
        return "شاخصی"
    if any(k in name_lower for k in ["بخشی", "صنعت"]):
        return "بخشی"
    if any(k in name_lower for k in ["مختلط", "تركيبي", "ترکیبی"]):
        return "مختلط"

    return "نامشخص"


def analyze_fund(row):
    """تحلیل یه صندوق"""
    try:
        symbol = str(row.get("Symbol", ""))
        name = str(row.get("Name", ""))

        if not is_fund(symbol, name):
            return None

        last = float(row.get("Last") or row.get("Close") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)
        nav = float(row.get("NAV") or 0)

        if last <= 0:
            return None

        # سفارشات
        bid_v1 = float(row.get("BidVolume1") or 0)
        ask_v1 = float(row.get("AskVolume1") or 0)
        has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
        has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)

        ratio = 1.0
        if vol_sell > 0:
            ratio = round(vol_buy / vol_sell, 2)

        fund_type = detect_fund_type(name, symbol)

        # حباب
        bubble = None
        if nav and nav > 0:
            bubble = round((last - nav) / nav * 100, 2)

        # امتیاز
        score = 0
        reasons = []

        # تغییر
        if change > 3:
            score += 30
            reasons.append(f"Rozane +{change:.1f}%")
        elif change > 1:
            score += 20
            reasons.append(f"Rozane +{change:.1f}%")
        elif change > 0:
            score += 10
            reasons.append(f"Rozane +{change:.1f}%")

        # صف
        if has_buy_queue:
            score += 25
            reasons.append("صف خرید")
        elif has_sell_queue:
            score += 5
            reasons.append("صف فروش")

        # نسبت
        if ratio > 2:
            score += 20
            reasons.append(f"Nesbat {ratio}")
        elif ratio > 1.5:
            score += 15
            reasons.append(f"Nesbat {ratio}")
        elif ratio > 1:
            score += 10
            reasons.append(f"Nesbat {ratio}")

        # حباب
        if bubble is not None:
            if bubble < -2:
                score += 15
                reasons.append(f"Kesr {bubble}%")
            elif bubble < 0:
                score += 10
                reasons.append(f"Kesr {bubble}%")
            elif bubble > 5:
                score -= 10
                reasons.append(f"Habab +{bubble}%")

        # نوع
        type_scores = {
            "درآمد ثابت": 10,
            "سهامی": 8,
            "کالایی": 7,
            "اهرمی": 5,
        }
        if fund_type in type_scores:
            score += type_scores[fund_type]
            reasons.append(f"{fund_type}")

        return {
            "symbol": symbol,
            "name": name,
            "ins_code": str(row.get("InsCode") or ""),
            "fund_type": fund_type,
            "last": last,
            "change": change,
            "nav": nav,
            "bubble": bubble,
            "ratio": ratio,
            "has_buy_queue": has_buy_queue,
            "has_sell_queue": has_sell_queue,
            "score": score,
            "reasons": reasons,
            "min_a": min_a,
            "max_a": max_a,
        }
    except Exception:
        return None


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  📊 اسکنر صندوق‌ها — نسخه ۲")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    safe_print("  🔍 تحلیل...")
    safe_print("")

    funds = []
    for _, row in df.iterrows():
        r = analyze_fund(row)
        if r:
            funds.append(r)

    safe_print(f"  ✅ {len(funds)} صندوق واقعی")
    safe_print("")

    # بر اساس نوع
    by_type = {}
    for f in funds:
        t = f["fund_type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(f)

    safe_print("  📊 بر اساس نوع:")
    for t, items in sorted(by_type.items()):
        safe_print(f"     {t}: {len(items)} صندوق")
    safe_print("")

    # بهترین
    funds.sort(key=lambda x: -x["score"])
    top = funds[:15]

    if not top:
        safe_print("  ❌ هیچ صندوقی پیدا نشد!")
        return

    safe_print("=" * 100)
    safe_print(f"  🏆 بهترین ۱۵ صندوق")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  {'#':<3} | {'نماد':<15} | {'نوع':<12} | {'قیمت':>10} | {'تغییر':>7} | {'حباب':>7} | {'امتیاز':>6}")
    safe_print("  " + "-" * 100)

    for i, f in enumerate(top, 1):
        bubble_str = f"{f['bubble']:+.1f}%" if f['bubble'] is not None else "—"

        safe_print(
            f"  {i:<3} | "
            f"{f['symbol'][:15]:<15} | "
            f"{f['fund_type'][:12]:<12} | "
            f"{int(f['last']):>10,} | "
            f"{f['change']:>+6.2f}% | "
            f"{bubble_str:>7} | "
            f"{f['score']:>4}/100"
        )

    safe_print("")

    # جزئیات
    for i, f in enumerate(top[:5], 1):
        safe_print(f"  ── {i}. {f['symbol']} ({f['name'][:40]}) ──")
        safe_print(f"     📌 نوع: {f['fund_type']}")
        safe_print(f"     💰 قیمت: {int(f['last']):,} ({f['change']:+.2f}%)")

        if f['nav']:
            safe_print(f"     📊 NAV: {int(f['nav']):,}")

        if f['bubble'] is not None:
            safe_print(f"     🎯 حباب/کسر: {f['bubble']:+.2f}%")

        safe_print(f"     🎯 امتیاز: {f['score']}/100")

        if f['has_buy_queue']:
            safe_print(f"     🟢 صف خرید")
        elif f['has_sell_queue']:
            safe_print(f"     🔴 صف فروش")

        safe_print("")
        safe_print(f"     📊 دلایل:")
        for r in f['reasons']:
            safe_print(f"        ✅ {r}")
        safe_print("")

    # ذخیره
    output = PROJECT_ROOT / "reports" / f"funds_v2_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_funds": len(funds),
            "by_type": {t: len(items) for t, items in by_type.items()},
            "top": top,
        }, f, ensure_ascii=False, indent=2)

    safe_print("=" * 100)
    safe_print(f"  💾 ذخیره: {output}")
    safe_print("=" * 100)


if __name__ == "__main__":
    main()
