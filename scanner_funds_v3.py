# scanner_funds_v3.py
# اسکنر هوشمند صندوق‌ها — نسخه ۳
# اجرا: python scanner_funds_v3.py

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

FUNDS_FILE = PROJECT_ROOT / "data" / "real_funds.json"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def detect_fund_type(name):
    """تشخیص دقیق نوع صندوق"""
    name_lower = str(name).lower()

    # اهرمی
    if "اهرمی" in name_lower or "اهرمي" in name_lower or "اهرم" in name_lower:
        return "اهرمی"

    # درآمد ثابت
    if any(k in name_lower for k in ["درآمد ثابت", "درامد ثابت", "درآمدثابت", "ثابت"]):
        return "درآمد ثابت"

    # طلا
    if any(k in name_lower for k in ["طلا", "زر", "گلد"]):
        return "طلا"

    # نقره
    if "نقره" in name_lower:
        return "نقره"

    # کالایی
    if "کالا" in name_lower or "كالا" in name_lower:
        return "کالایی"

    # سهامی
    if any(k in name_lower for k in ["سهامي", "سهامی", "سهام"]):
        return "سهامی"

    # شاخصی
    if "شاخص" in name_lower:
        return "شاخصی"

    # بخشی
    if any(k in name_lower for k in ["بخشي", "بخشی", "صنعت", "صنايع"]):
        return "بخشی"

    # مختلط
    if any(k in name_lower for k in ["مختلط", "تركيبي", "ترکیبی"]):
        return "مختلط"

    # املاک
    if "املاك" in name_lower or "املاک" in name_lower:
        return "املاک"

    # اندوخته
    if "اندوخته" in name_lower:
        return "اندوخته"

    # صندوق در صندوق
    if "صندوق در صندوق" in name_lower:
        return "صندوق در صندوق"

    return "نامشخص"


def analyze_fund(row):
    """تحلیل یه صندوق"""
    try:
        symbol = str(row.get("Symbol", ""))
        name = str(row.get("Name", ""))

        if not symbol or not name:
            return None

        # حذف حق تقدم
        if symbol.endswith("3") or symbol.endswith("ح"):
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

        fund_type = detect_fund_type(name)

        # حباب/کسر
        bubble = None
        if nav and nav > 0:
            bubble = round((last - nav) / nav * 100, 2)

        # امتیاز
        score = 0
        reasons = []

        # تغییر روزانه
        if change > 3:
            score += 30
            reasons.append(f"Rozane +{change:.1f}%")
        elif change > 1:
            score += 20
            reasons.append(f"Rozane +{change:.1f}%")
        elif change > 0:
            score += 10
            reasons.append(f"Rozane +{change:.1f}%")
        elif change < -3:
            score += 25
            reasons.append(f"Rozane {change:.1f}% (فرصت)")
        elif change < -1:
            score += 15
            reasons.append(f"Rozane {change:.1f}%")

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

        # حباب/کسر
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

        # نوع صندوق
        type_scores = {
            "درآمد ثابت": 10,
            "سهامی": 8,
            "کالایی": 7,
            "طلا": 8,
            "نقره": 7,
            "بخشی": 6,
            "شاخصی": 5,
            "اهرمی": 3,
            "مختلط": 5,
            "املاک": 5,
        }
        if fund_type in type_scores:
            score += type_scores[fund_type]

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
    safe_print("  📊 اسکنر هوشمند صندوق‌ها — نسخه ۳")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    if not FUNDS_FILE.exists():
        safe_print(f"  ❌ {FUNDS_FILE} پیدا نشد!")
        safe_print("  اول `find_real_funds.py` رو اجرا کن!")
        return

    # لیست صندوق‌ها
    funds_list = json.loads(FUNDS_FILE.read_text(encoding="utf-8"))
    safe_print(f"  📊 {len(funds_list)} صندوق در لیست")
    safe_print("")

    # دریافت داده
    safe_print("  📡 دریافت داده زنده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    # نقشه صندوق‌ها
    fund_codes = {f["ins_code"]: f for f in funds_list}

    # تحلیل
    safe_print("  🔍 تحلیل...")
    safe_print("")

    funds = []
    for _, row in df.iterrows():
        ins_code = str(row.get("InsCode") or "")

        # فقط صندوق‌های توی لیست
        if ins_code not in fund_codes:
            continue

        r = analyze_fund(row)
        if r:
            funds.append(r)

    safe_print(f"  ✅ {len(funds)} صندوق تحلیل شد")
    safe_print("")

    # گروه‌بندی بر اساس نوع
    by_type = {}
    for f in funds:
        t = f["fund_type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(f)

    safe_print("  📊 بر اساس نوع:")
    for t, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        safe_print(f"     {t:20} : {len(items):3} صندوق")
    safe_print("")

    # مرتب‌سازی
    funds.sort(key=lambda x: -x["score"])
    top = funds[:20]

    if not top:
        safe_print("  ❌ هیچ صندوقی پیدا نشد!")
        return

    # نمایش
    safe_print("=" * 100)
    safe_print(f"  🏆 بهترین ۲۰ صندوق")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  {'#':<3} | {'نماد':<15} | {'نوع':<15} | {'قیمت':>10} | {'تغییر':>7} | {'امتیاز':>6}")
    safe_print("  " + "-" * 100)

    for i, f in enumerate(top, 1):
        safe_print(
            f"  {i:<3} | "
            f"{f['symbol'][:15]:<15} | "
            f"{f['fund_type'][:15]:<15} | "
            f"{int(f['last']):>10,} | "
            f"{f['change']:>+6.2f}% | "
            f"{f['score']:>4}/100"
        )

    safe_print("")

    # ذخیره
    output = PROJECT_ROOT / "reports" / f"funds_v3_{datetime.now().strftime('%Y-%m-%d')}.json"
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
