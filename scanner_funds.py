# scanner_funds.py
# اسکنر صندوق‌ها (ETF)
# اجرا: python scanner_funds.py

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


def detect_fund_type(name, symbol):
    """تشخیص نوع صندوق"""
    name_lower = str(name).lower()
    symbol_lower = str(symbol).lower()

    # صندوق اهرمی
    if "اهرمی" in name_lower or "اهرمي" in name_lower or "lever" in name_lower:
        return "اهرمی"

    # صندوق درآمد ثابت
    if "ثابت" in name_lower or "درآمد" in name_lower or "درامد" in name_lower:
        return "درآمد ثابت"

    # صندوق سهامی
    if "سهامی" in name_lower or "سهامي" in name_lower:
        return "سهامی"

    # صندوق کالایی
    if "طلا" in name_lower or "نقره" in name_lower or "کالا" in name_lower:
        return "کالایی"

    # صندوق شاخصی
    if "شاخص" in name_lower or "شاخصی" in name_lower or "index" in name_lower:
        return "شاخصی"

    # صندوق بخشی
    if "بخشی" in name_lower or "صنعت" in name_lower:
        return "بخشی"

    # صندوق مختلط
    if "مختلط" in name_lower or "تركيبي" in name_lower:
        return "مختلط"

    return "نامشخص"


def analyze_fund(row):
    """تحلیل یه صندوق"""
    try:
        symbol = str(row.get("Symbol", ""))
        name = str(row.get("Name", ""))
        ins_code = str(row.get("InsCode") or "")

        if not symbol:
            return None

        # فیلتر: صندوق‌ها معمولاً با "ص" شروع می‌شن یا اسمشون "صندوق" داره
        is_fund = (
            symbol.startswith("ص") or
            "صندوق" in name or
            "ص." in name or
            "س." in name
        )

        if not is_fund:
            return None

        # قیمت
        last = float(row.get("Last") or row.get("Close") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)
        nav = float(row.get("NAV") or 0)

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

        ratio = 1.0
        if vol_sell > 0:
            ratio = round(vol_buy / vol_sell, 2)

        # نوع صندوق
        fund_type = detect_fund_type(name, symbol)

        # حباب/کسر
        bubble = None
        if nav and nav > 0:
            bubble = round((last - nav) / nav * 100, 2)

        # امتیاز
        score = 0
        reasons = []

        # ۱. تغییر روزانه (30)
        if change > 3:
            score += 30
            reasons.append(f"Rozane +{change:.1f}% (30)")
        elif change > 1:
            score += 20
            reasons.append(f"Rozane +{change:.1f}% (20)")
        elif change > 0:
            score += 10
            reasons.append(f"Rozane +{change:.1f}% (10)")
        elif change < -3:
            score += 25
            reasons.append(f"Rozane {change:.1f}% (فرصت) (25)")
        elif change < -1:
            score += 15
            reasons.append(f"Rozane {change:.1f}% (15)")

        # ۲. صف (25)
        if has_buy_queue:
            score += 25
            reasons.append("صف خرید (25)")
        elif has_sell_queue:
            score += 5
            reasons.append("صف فروش (5)")

        # ۳. نسبت خرید/فروش (20)
        if ratio > 2:
            score += 20
            reasons.append(f"Nesbat {ratio} (20)")
        elif ratio > 1.5:
            score += 15
            reasons.append(f"Nesbat {ratio} (15)")
        elif ratio > 1:
            score += 10
            reasons.append(f"Nesbat {ratio} (10)")

        # ۴. حباب/کسر (15)
        if bubble is not None:
            if bubble < -2:
                score += 15
                reasons.append(f"Kesr {bubble}% (15)")
            elif bubble < 0:
                score += 10
                reasons.append(f"Kesr {bubble}% (10)")
            elif bubble > 5:
                score -= 10
                reasons.append(f"Habab +{bubble}% (-10)")

        # ۵. نوع صندوق (10)
        if fund_type == "درآمد ثابت":
            score += 10
            reasons.append("درآمد ثابت (10)")
        elif fund_type == "اهرمی":
            score += 5
            reasons.append("اهرمی (5)")
        elif fund_type == "سهامی":
            score += 8
            reasons.append("سهامی (8)")
        elif fund_type == "کالایی":
            score += 7
            reasons.append("کالایی (7)")

        return {
            "symbol": symbol,
            "name": name,
            "ins_code": ins_code,
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
    safe_print("  📊 اسکنر صندوق‌ها (ETF)")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
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
    safe_print("  🔍 تحلیل صندوق‌ها...")
    safe_print("")

    funds = []
    for _, row in df.iterrows():
        r = analyze_fund(row)
        if r:
            funds.append(r)

    safe_print(f"  ✅ {len(funds)} صندوق")
    safe_print("")

    # گروه‌بندی بر اساس نوع
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

    # مرتب‌سازی
    funds.sort(key=lambda x: -x["score"])
    top = funds[:15]

    # نمایش
    safe_print("=" * 100)
    safe_print(f"  🏆 بهترین ۱۵ صندوق")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  {'#':<3} | {'نماد':<12} | {'نوع':<12} | {'قیمت':>10} | {'تغییر':>7} | {'حباب':>7} | {'امتیاز':>6}")
    safe_print("  " + "-" * 100)

    for i, f in enumerate(top, 1):
        bubble_str = f"{f['bubble']:+.1f}%" if f['bubble'] is not None else "—"

        safe_print(
            f"  {i:<3} | "
            f"{f['symbol'][:12]:<12} | "
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
            bubble_emoji = "🔴" if f['bubble'] > 3 else ("🟢" if f['bubble'] < -2 else "🟡")
            safe_print(f"     {bubble_emoji} حباب/کسر: {f['bubble']:+.2f}%")

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
    output = PROJECT_ROOT / "reports" / f"funds_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_funds": len(funds),
            "top": top,
        }, f, ensure_ascii=False, indent=2)

    safe_print("=" * 100)
    safe_print(f"  💾 ذخیره: {output}")
    safe_print("=" * 100)


if __name__ == "__main__":
    main()
