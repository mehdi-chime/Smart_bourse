# check_history_json.py
# چک ساختار JSONهای تاریخچه
# اجرا: python check_history_json.py

import os
import sys
import json
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
HISTORY_DIR = PROJECT_ROOT / "data" / "history"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 چک ساختار JSONهای تاریخچه")
    safe_print("=" * 80)
    safe_print("")

    if not HISTORY_DIR.exists():
        safe_print("  ❌ پوشه history پیدا نشد!")
        return

    # لیست فایل‌ها
    json_files = list(HISTORY_DIR.glob("*_history.json"))
    safe_print(f"  📊 {len(json_files)} فایل JSON")
    safe_print("")

    # چک ۳ فایل اول
    for f in json_files[:3]:
        safe_print(f"  📄 {f.name}")
        safe_print(f"     حجم: {f.stat().st_size:,} bytes")
        
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            
            safe_print(f"     نوع: {type(data).__name__}")
            
            if isinstance(data, list):
                safe_print(f"     تعداد آیتم: {len(data)}")
                if len(data) > 0:
                    first = data[0]
                    safe_print(f"     نوع آیتم اول: {type(first).__name__}")
                    if isinstance(first, dict):
                        safe_print(f"     کلیدها: {list(first.keys())}")
                        safe_print(f"     نمونه:")
                        for k, v in list(first.items())[:8]:
                            safe_print(f"        {k}: {v}")
            elif isinstance(data, dict):
                safe_print(f"     کلیدها: {list(data.keys())}")
                safe_print(f"     نمونه:")
                for k, v in list(data.items())[:8]:
                    safe_print(f"        {k}: {v}")
        except Exception as e:
            safe_print(f"     ❌ خطا: {e}")
        
        safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
