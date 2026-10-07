# investigate_rahavard.py
# بررسی سایت rahavard365.com
# اجرا: python investigate_rahavard.py

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


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 بررسی سایت rahavard365.com")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    import requests

    # هدرها (مثل مرورگر)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    }

    # ۱. صفحه اصلی
    safe_print("  📄 ۱. چک صفحه اصلی...")
    try:
        r = requests.get(
            "https://rahavard365.com/",
            headers=headers,
            timeout=15,
        )
        safe_print(f"     Status: {r.status_code}")
        safe_print(f"     Size: {len(r.text)} b")
        safe_print(f"     Content-Type: {r.headers.get('Content-Type')}")
    except Exception as e:
        safe_print(f"     ❌ {e}")
    safe_print("")

    # ۲. صفحه closedassets
    safe_print("  📄 ۲. چک /closedassets...")
    try:
        r = requests.get(
            "https://rahavard365.com/closedassets",
            headers=headers,
            timeout=15,
        )
        safe_print(f"     Status: {r.status_code}")
        safe_print(f"     Size: {len(r.text)} b")
        safe_print(f"     Content-Type: {r.headers.get('Content-Type')}")

        # ذخیره HTML
        output = PROJECT_ROOT / "data" / "rahavard_closedassets.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(r.text, encoding="utf-8")
        safe_print(f"     💾 ذخیره: {output}")

        # جستجوی API
        safe_print("")
        safe_print("     🔍 جستجوی API:")
        if "api" in r.text.lower():
            safe_print(f"        ✅ 'api' در HTML پیدا شد")
        if "json" in r.text.lower():
            safe_print(f"        ✅ 'json' در HTML پیدا شد")
        if "fetch" in r.text.lower():
            safe_print(f"        ✅ 'fetch' در HTML پیدا شد")
        if "axios" in r.text.lower():
            safe_print(f"        ✅ 'axios' در HTML پیدا شد")

    except Exception as e:
        safe_print(f"     ❌ {e}")
    safe_print("")

    # ۳. چک APIهای محتمل
    safe_print("  📄 ۳. چک APIهای محتمل...")

    api_urls = [
        "https://rahavard365.com/api/closedassets",
        "https://rahavard365.com/api/v1/closedassets",
        "https://rahavard365.com/api/assets/closed",
        "https://api.rahavard365.com/closedassets",
        "https://rahavard365.com/api/symbols/closed",
    ]

    for url in api_urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            safe_print(f"     {url}: {r.status_code}")

            if r.status_code == 200:
                safe_print(f"        ✅ {r.text[:200]}")
        except Exception as e:
            safe_print(f"     {url}: ❌ {e}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
