# back_to_old_strategy.py
# برگشت به استراتژی قبلی (بهتر)
# اجرا: python back_to_old_strategy.py

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


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔄 برگشت به استراتژی قبلی")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  📌 چرا؟")
    safe_print("     1. RSI پایین بهتره")
    safe_print("     2. P/E پایین بهتره")
    safe_print("     3. صف خرید فریبنده‌ست")
    safe_print("     4. RSI بالا = اشباع")
    safe_print("")

    safe_print("  🎯 استراتژی قبلی:")
    safe_print("     - P/E < 15")
    safe_print("     - RSI 10-50")
    safe_print("     - ATR > 2.5%")
    safe_print("     - حقوقی خریدار")
    safe_print("     - حجم > 500,000")
    safe_print("")

    safe_print("  📁 فایل اصلی:")
    safe_print("     - smart_scanner_v8.py")
    safe_print("")

    safe_print("  📌 دستور:")
    safe_print("     python smart_scanner_v8.py")
    safe_print("")

    safe_print("=" * 80)


if __name__ == "__main__":
    main()
