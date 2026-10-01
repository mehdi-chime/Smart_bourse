# scan_project.py
# اسکن کامل پروژه Smart_Bourse
# اجرا: python scan_project.py

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
    safe_print("=" * 100)
    safe_print(f"  📊 اسکن کامل پروژه Smart_Bourse")
    safe_print(f"  📁 {PROJECT_ROOT}")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    if not PROJECT_ROOT.exists():
        safe_print(f"  ❌ مسیر پیدا نشد: {PROJECT_ROOT}")
        return

    # ═══════════════════════════════════════════════════════
    # ۱. شمارش فایل‌ها
    # ═══════════════════════════════════════════════════════
    py_files = list(PROJECT_ROOT.rglob("*.py"))
    json_files = list(PROJECT_ROOT.rglob("*.json"))
    txt_files = list(PROJECT_ROOT.rglob("*.txt"))
    md_files = list(PROJECT_ROOT.rglob("*.md"))
    csv_files = list(PROJECT_ROOT.rglob("*.csv"))
    db_files = list(PROJECT_ROOT.rglob("*.db"))
    log_files = list(PROJECT_ROOT.rglob("*.log"))
    bat_files = list(PROJECT_ROOT.rglob("*.bat"))
    html_files = list(PROJECT_ROOT.rglob("*.html"))

    all_files = [f for f in PROJECT_ROOT.rglob("*") if f.is_file()]

    safe_print("  📊 آمار کلی:")
    safe_print(f"     کل فایل‌ها:     {len(all_files):>6,}")
    safe_print(f"     فایل‌های پایتون: {len(py_files):>6,}")
    safe_print(f"     فایل‌های JSON:   {len(json_files):>6,}")
    safe_print(f"     فایل‌های TXT:    {len(txt_files):>6,}")
    safe_print(f"     فایل‌های MD:     {len(md_files):>6,}")
    safe_print(f"     فایل‌های CSV:    {len(csv_files):>6,}")
    safe_print(f"     فایل‌های DB:     {len(db_files):>6,}")
    safe_print(f"     فایل‌های LOG:    {len(log_files):>6,}")
    safe_print(f"     فایل‌های BAT:    {len(bat_files):>6,}")
    safe_print(f"     فایل‌های HTML:   {len(html_files):>6,}")
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۲. خطوط کد
    # ═══════════════════════════════════════════════════════
    total_lines = 0
    for f in py_files:
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as file:
                total_lines += len(file.readlines())
        except:
            pass

    safe_print(f"  📝 کل خطوط کد پایتون: {total_lines:,}")
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۳. پوشه‌های اصلی
    # ═══════════════════════════════════════════════════════
    safe_print("  📁 پوشه‌های اصلی:")
    safe_print("")

    for item in sorted(PROJECT_ROOT.iterdir()):
        if item.is_dir():
            sub_files = list(item.rglob("*"))
            sub_py = len([f for f in sub_files if f.suffix == ".py" and f.is_file()])
            sub_all = len([f for f in sub_files if f.is_file()])

            safe_print(f"     📁 {item.name:<25} ({sub_py} py / {sub_all} کل)")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۴. فایل‌های مهم ریشه
    # ═══════════════════════════════════════════════════════
    safe_print("  📄 فایل‌های مهم ریشه:")
    safe_print("")

    important = [
        "main.py", "config.py", "requirements.txt", "README.md",
        "alert_config.py", "project_config.py", "daily_runner.py",
        "auto_trader.py", "auto_push.py", "chatgpt_bridge.py",
        "Smart_Bourse_RoadMap.txt", "DeepSeek_RoadMap.txt",
    ]

    for name in important:
        f = PROJECT_ROOT / name
        if f.exists():
            size = f.stat().st_size
            safe_print(f"     ✅ {name:<35} ({size:,} bytes)")
        else:
            safe_print(f"     ❌ {name:<35} (نیست)")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۵. فایل‌های alert_config (مهم برای ایتا)
    # ═══════════════════════════════════════════════════════
    safe_print("  🔑 فایل‌های alert_config (مهم برای ایتا):")
    safe_print("")

    alert_configs = list(PROJECT_ROOT.rglob("alert_config.py"))
    if alert_configs:
        for f in alert_configs:
            safe_print(f"     ✅ {str(f.relative_to(PROJECT_ROOT))}")
    else:
        safe_print("     ❌ پیدا نشد!")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۶. نسخه‌های مختلف فایل‌ها
    # ═══════════════════════════════════════════════════════
    safe_print("  🔄 نسخه‌های مختلف:")
    safe_print("")

    patterns = ["smart_scanner", "smart_bourse", "school_mode", "tomorrow",
                "night_check", "golden_scanner", "install_school"]

    for pattern in patterns:
        matches = list(PROJECT_ROOT.glob(f"*{pattern}*.py"))
        if matches:
            safe_print(f"     📌 {pattern}:")
            for m in matches:
                safe_print(f"        - {m.name}")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۷. فایل‌های JSON داده
    # ═══════════════════════════════════════════════════════
    safe_print("  📊 فایل‌های JSON داده (پوشه data):")
    safe_print("")

    data_dir = PROJECT_ROOT / "data"
    if data_dir.exists():
        for sub in sorted(data_dir.iterdir()):
            if sub.is_dir():
                jsons = list(sub.glob("*.json"))
                if jsons:
                    safe_print(f"     📁 data/{sub.name}/ ({len(jsons)} فایل)")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۸. دیتابیس‌ها
    # ═══════════════════════════════════════════════════════
    safe_print("  🗄️ دیتابیس‌ها:")
    safe_print("")

    if db_files:
        for f in db_files:
            size = f.stat().st_size
            rel_path = str(f.relative_to(PROJECT_ROOT))
            safe_print(f"     ✅ {rel_path:<50} ({size:,} bytes)")
    else:
        safe_print("     ❌ دیتابیس پیدا نشد!")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۹. لاگ‌های اخیر
    # ═══════════════════════════════════════════════════════
    safe_print("  📝 لاگ‌های اخیر:")
    safe_print("")

    if log_files:
        for f in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            size = f.stat().st_size
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            rel_path = str(f.relative_to(PROJECT_ROOT))
            safe_print(f"     📄 {rel_path:<45} ({size:,} b, {mtime})")
    else:
        safe_print("     ❌ لاگ پیدا نشد!")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ۱۰. ذخیره در JSON
    # ═══════════════════════════════════════════════════════
    output = PROJECT_ROOT / "project_scan.json"

    scan_data = {
        "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project_root": str(PROJECT_ROOT),
        "total_files": len(all_files),
        "python_files": len(py_files),
        "json_files": len(json_files),
        "total_lines": total_lines,
        "directories": [d.name for d in PROJECT_ROOT.iterdir() if d.is_dir()],
        "python_files_list": [str(f.relative_to(PROJECT_ROOT)) for f in py_files],
        "db_files": [str(f.relative_to(PROJECT_ROOT)) for f in db_files],
        "log_files": [str(f.relative_to(PROJECT_ROOT)) for f in log_files],
        "alert_configs": [str(f.relative_to(PROJECT_ROOT)) for f in alert_configs],
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(scan_data, f, ensure_ascii=False, indent=2)

    safe_print("=" * 100)
    safe_print(f"  💾 نتیجه ذخیره شد: {output}")
    safe_print("=" * 100)
    safe_print("")


if __name__ == "__main__":
    main()
