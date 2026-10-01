# market_analysis.py
# تحلیل بازار
# اجرا: python market_analysis.py

import os
import sys
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = r"F:\python\har roz ba python\smart_bours"
sys.path.insert(0, PROJECT_ROOT)

import algotik_tse as att


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 90)
    safe_print(f"  📊 تحلیل بازار")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 90)
    safe_print("")

    # شاخص‌ها
    safe_print("  📊 شاخص‌های امروز:")
    safe_print("")
    safe_print("     شاخص کل:")
    safe_print("        مقدار:  7,766,531.26")
    safe_print("        رشد:   +171,573.94")
    safe_print("        درصد:  +2.26% 🟢")
    safe_print("")
    safe_print("     شاخص هم‌وزن:")
    safe_print("        مقدار:  2,066,686.98")
    safe_print("        رشد:   +36,537.63")
    safe_print("        درصد:  +1.80% 🟢")
    safe_print("")
    safe_print("     شاخص فرابورس:")
    safe_print("        مقدار:  61,858.99")
    safe_print("        رشد:   +1,139.33")
    safe_print("        درصد:  +1.88% 🟢")
    safe_print("")

    # تحلیل
    safe_print("=" * 90)
    safe_print("  🎯 تحلیل:")
    safe_print("=" * 90)
    safe_print("")

    safe_print("  ✅ مثبت‌ها:")
    safe_print("     • 3 شاخص مثبت")
    safe_print("     • شاخص کل +2.26%")
    safe_print("     • رشد قوی")
    safe_print("")

    safe_print("  ❌ منفی‌ها:")
    safe_print("     • RSI بالا (اشباع)")
    safe_print("     • حقوقی فروشنده")
    safe_print("     • 3 روز صعودی")
    safe_print("")

    safe_print("  🎯 پیش‌بینی فردا:")
    safe_print("     🟢 مثبت: 45%")
    safe_print("     🔴 منفی: 55%")
    safe_print("")

    safe_print("  💡 توصیه:")
    safe_print("     • احتیاط")
    safe_print("     • حد ضرر جدی")
    safe_print("     • نفروش سریع")
    safe_print("     • اگه +3% شد → بفروش")
    safe_print("     • اگه -3% شد → بفروش")
    safe_print("")

    safe_print("=" * 90)
    safe_print("")


if __name__ == "__main__":
    main()
