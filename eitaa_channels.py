# eitaa_channels.py
# خواندن کانال‌های ایتا
# اجرا: python eitaa_channels.py

import os
import sys
import json
import requests
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

# ═══════════════════════════════════════════════════════════
# کانال‌های ایتا (بورسی)
# ═══════════════════════════════════════════════════════════
CHANNELS = [
    # اگه کانال ایتا داری، اینجا بذار
    # "bourse24",
    # "rasadchi",
]

OUTPUT_DIR = PROJECT_ROOT / "data" / "eitaa_channels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  Eitaa Channels Reader")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  ⚠️ ایتا API عمومی نداره")
    safe_print("  ⚠️ فقط با ربات خودمون می‌شه")
    safe_print("")
    safe_print("  راه‌حل:")
    safe_print("  ۱. تو ایتا، کانال‌های بورسی رو دنبال کن")
    safe_print("  ۲. خودت تحلیل کن")
    safe_print("  ۳. از اسکریپت‌های خودمون استفاده کن")
    safe_print("")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
