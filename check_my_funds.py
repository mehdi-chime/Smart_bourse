# check_my_funds.py
# بررسی صندوق‌های من — کامل
# اجرا: python check_my_funds.py

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


# ═══════════════════════════════════════════════════════════
# صندوق‌های من
# ═══════════════════════════════════════════════════════════

MY_FUNDS = [
    ("34144395039913458", "عيار", "صندوق طلاي عيار مفيد"),
    ("17248898258246807", "درنا", "صندوق پشتوانه طلاي درنا"),
    ("17914401175772326", "اهرم", "صندوق سهامي کاريزما-اهرمي"),
    ("55308018877404137", "سام", "صندوق درآمد ثابت سام-د"),
    ("3927545069816217", "سپينود", "صندوق سهامي سپينود-س"),
]


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  📊 بررسی صندوق‌های من")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    if not MY_FUNDS:
        safe_print("  ⚠️ MY_FUNDS خالیه!")
        safe_print("  توی کد، صندوق‌هات رو بذار.")
        return

    df = att.get_live_market()
    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print(f"  📊 {len(df)} سهم")
    safe_print("")

    results = []

    for ins_code, symbol, name in MY_FUNDS:
        safe_print(f"  🔍 {symbol}...")

        found = None
        for _, row in df.iterrows():
            if str(row.get("InsCode")) == ins_code:
                found = row
                break

        if found is None:
            safe_print(f"     ❌ پیدا نشد")
            safe_print("")
            continue

        last = float(found.get("Last") or 0)
        change = float(found.get("ChangePct") or 0)
        nav = float(found.get("NAV") or 0)
        min_a = float(found.get("MinAllowed") or 0)
        max_a = float(found.get("MaxAllowed") or 0)

        bubble = None
        if nav and nav > 0:
            bubble = (last - nav) / nav * 100

        bid_v1 = float(found.get("BidVolume1") or 0)
        ask_v1 = float(found.get("AskVolume1") or 0)
        has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
        has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

        result = {
            "symbol": symbol,
            "name": found.get("Name"),
            "last": last,
            "change": change,
            "nav": nav,
            "bubble": bubble,
            "min_a": min_a,
            "max_a": max_a,
            "has_buy_queue": has_buy_queue,
            "has_sell_queue": has_sell_queue,
        }
        results.append(result)

        safe_print(f"     ✅ {found.get('Name')}")
        safe_print(f"     💰 قیمت: {int(last):,} ({change:+.2f}%)")

        if nav:
            bubble_emoji = "🔴" if bubble > 3 else ("🟢" if bubble < -2 else "🟡")
            safe_print(f"     {bubble_emoji} NAV: {int(nav):,} | حباب: {bubble:+.2f}%")

        if has_buy_queue:
            safe_print(f"     🟢 صف خرید")
        elif has_sell_queue:
            safe_print(f"     🔴 صف فروش")

        safe_print("")

    # جدول خلاصه
    if results:
        safe_print("=" * 100)
        safe_print("  📊 جدول خلاصه")
        safe_print("=" * 100)
        safe_print("")
        safe_print(f"  {'#':<3} | {'نماد':<15} | {'قیمت':>10} | {'تغییر':>7} | {'حباب':>8} | {'صف':>5}")
        safe_print("  " + "-" * 90)

        for i, r in enumerate(results, 1):
            bubble_str = f"{r['bubble']:+.1f}%" if r['bubble'] is not None else "—"
            queue = "BUY" if r['has_buy_queue'] else ("SELL" if r['has_sell_queue'] else "---")

            safe_print(
                f"  {i:<3} | "
                f"{r['symbol'][:15]:<15} | "
                f"{int(r['last']):>10,} | "
                f"{r['change']:>+6.2f}% | "
                f"{bubble_str:>8} | "
                f"{queue:>5}"
            )

    safe_print("")
    safe_print("=" * 100)


if __name__ == "__main__":
    main()
