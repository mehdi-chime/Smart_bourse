# check_eitaa_v3.py
# بررسی وضعیت ایتا (نسخه نهایی)
# اجرا: python check_eitaa_v3.py

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")

print()
print("=" * 80)
print("  🔍 بررسی وضعیت ایتا (v3)")
print("=" * 80)
print()
print(f"  📁 PROJECT_ROOT: {PROJECT_ROOT}")
print()

# ۱. چک فایل‌ها
print("  📄 چک فایل‌ها:")
print()

files = [
    "eitaa/eitaa_bot.py",
    "scanner/alert_config.py",
    "scanner/smart_alert.py",
    "scanner/alert_monitor.py",
    "scanner/portfolio_alert.py",
    "scanner/auto_portfolio_alert.py",
]

for rel in files:
    full = PROJECT_ROOT / rel
    if full.exists():
        size = full.stat().st_size
        print(f"     ✅ {rel} ({size:,} بایت)")
    else:
        print(f"     ❌ {rel}")

print()

# ۲. محتوای eitaa_bot.py
eitaa_file = PROJECT_ROOT / "eitaa" / "eitaa_bot.py"
if eitaa_file.exists():
    print("=" * 80)
    print("  📄 محتوای eitaa_bot.py")
    print("=" * 80)
    print()
    with open(eitaa_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(content)
    print()
    print("=" * 80)
    print()

# ۳. محتوای alert_config.py
alert_file = PROJECT_ROOT / "scanner" / "alert_config.py"
if alert_file.exists():
    print("=" * 80)
    print("  📄 محتوای alert_config.py")
    print("=" * 80)
    print()
    with open(alert_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(content)
    print()
    print("=" * 80)
    print()

# ۴. جستجوی فایل‌های ایتا
print("  🔍 جستجوی فایل‌های ایتا:")
print()
for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
    dirnames[:] = [d for d in dirnames if d not in {'.git', '__pycache__', 'venv', 'data', 'logs', 'backup'}]
    for f in filenames:
        if 'eitaa' in f.lower() or 'alert' in f.lower():
            full = Path(dirpath) / f
            rel = full.relative_to(PROJECT_ROOT)
            print(f"     📄 {rel} ({full.stat().st_size:,} بایت)")

print()
print("=" * 80)
print("  ✅ پایان")
print("=" * 80)
print()
