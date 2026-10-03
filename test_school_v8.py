# test_school_v8.py
# تست کامل school_mode_v8
# اجرا: python test_school_v8.py

import os
import sys
from pathlib import Path

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
    safe_print("  🧪 تست کامل school_mode_v8")
    safe_print("=" * 80)
    safe_print("")

    # ۱. import
    safe_print("  📦 import...")
    try:
        import school_mode_v8
        safe_print("     ✅ import موفق")
    except Exception as e:
        safe_print(f"     ❌ {e}")
        return
    safe_print("")

    # ۲. تست send_eitaa
    safe_print("  📱 تست send_eitaa...")
    try:
        ok = school_mode_v8.send_eitaa("🧪 تست ۱: send_eitaa")
        safe_print(f"     {'✅' if ok else '❌'} {ok}")
    except Exception as e:
        safe_print(f"     ❌ {e}")
    safe_print("")

    # ۳. تست send_market_status
    safe_print("  📈 تست send_market_status...")
    try:
        ok = school_mode_v8.send_market_status()
        safe_print(f"     {'✅' if ok else '❌'} {ok}")
    except Exception as e:
        safe_print(f"     ❌ {e}")
    safe_print("")

    # ۴. تست run_scanner
    safe_print("  🔍 تست run_scanner...")
    safe_print("     (ممکنه ۱-۲ دقیقه طول بکشه)")
    try:
        ok = school_mode_v8.run_scanner()
        safe_print(f"     {'✅' if ok else '⚠️'} {ok}")
    except Exception as e:
        safe_print(f"     ❌ {e}")
    safe_print("")

    # ۵. تست send_scanner_result
    safe_print("  📊 تست send_scanner_result...")
    try:
        ok = school_mode_v8.send_scanner_result()
        safe_print(f"     {'✅' if ok else '⚠️'} {ok}")
    except Exception as e:
        safe_print(f"     ❌ {e}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
