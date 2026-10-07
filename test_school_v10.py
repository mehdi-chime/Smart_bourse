# test_school_v10.py
# تست v10 (بدون چک ساعت)
# اجرا: python test_school_v10.py

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
sys.path.insert(0, str(PROJECT_ROOT))


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🧪 تست v10 (دستی)")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # import از v10
    import school_mode_v10 as v10

    # ۱. تحلیل بازار
    safe_print("  📊 تحلیل بازار...")
    market = v10.analyze_market()

    if not market:
        safe_print("  ❌ خطا")
        return

    safe_print(f"     کل: {market['total']}")
    safe_print(f"     🟢 مثبت: {market['positive']}")
    safe_print(f"     🔴 منفی: {market['negative']}")
    safe_print(f"     📊 درصد: {market['market_pct']}%")
    safe_print("")

    # ۲. بازه داینامیک
    MIN_RSI, MAX_RSI, state = v10.get_dynamic_rsi_range(market)
    safe_print(f"  🎯 بازه RSI: {MIN_RSI}-{MAX_RSI}")
    safe_print(f"  📊 وضعیت: {state}")
    safe_print("")

    # ۳. اسکن
    safe_print("  🔍 اسکن...")
    candidates = v10.scan_stocks(market)
    safe_print(f"     ✅ {len(candidates)} سهم")
    safe_print("")

    # ۴. نمایش
    for i, s in enumerate(candidates, 1):
        safe_print(f"  {i}. {s['symbol']}: {s['rsi']} (امتیاز {s['score']})")
    safe_print("")

    # ۵. ارسال
    if candidates:
        safe_print("  📱 ارسال به ایتا...")
        msg = v10.build_message(candidates, market, state, MIN_RSI, MAX_RSI)
        if v10.send_eitaa(msg):
            safe_print("     ✅ ارسال شد")
    safe_print("")

    safe_print("=" * 80)


if __name__ == "__main__":
    main()
