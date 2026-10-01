# shakhes_check.py
# بررسی شاخص کل
# اجرا: python shakhes_check.py

import os
import sys
import requests
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def get_shakhes():
    """شاخص کل از TSETMC"""
    try:
        url = "https://old.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return None

        # شاخص کل از data
        # اینجا باید parse کنی
        return r.text[:200]

    except Exception as e:
        return f"ERR: {e}"


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  📊 بررسی شاخص کل")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  📡 دریافت شاخص...")
    result = get_shakhes()

    if result:
        safe_print(f"  ✅ {result[:100]}")
    else:
        safe_print("  ❌ خطا")

    safe_print("")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
