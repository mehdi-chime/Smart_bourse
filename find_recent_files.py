# find_recent_files.py
# شناسایی فایل‌های جدید (۱۰ روز اخیر)
# اجرا: python find_recent_files.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
OUTPUT_FILE = PROJECT_ROOT / "recent_files_report.txt"

# چند روز اخیر؟
DAYS = 10

# پوشه‌هایی که نباید بررسی بشن
SKIP_DIRS = [
    "__pycache__", ".git", ".idea", ".vscode",
    "_for_deepseek", "backup", "node_modules",
    "data/history", "data/real_flow", "data/live_records",
    "logs", "reports/chatgpt_bridge",
    "reports/diagnostics", "reports/tal",
]


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def should_skip(path):
    """چک کن آیا باید رد بشه"""
    path_str = str(path).lower()
    for skip in SKIP_DIRS:
        if skip.lower() in path_str:
            return True
    return False


def get_recent_files(days=10):
    """فایل‌های جدید رو پیدا کن"""
    cutoff = datetime.now() - timedelta(days=days)
    
    recent = []
    all_files = []
    
    for f in PROJECT_ROOT.rglob("*"):
        if not f.is_file():
            continue
        if should_skip(f):
            continue
        
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            size = f.stat().st_size
            rel_path = str(f.relative_to(PROJECT_ROOT))
            
            file_info = {
                "path": rel_path,
                "name": f.name,
                "size": size,
                "mtime": mtime,
                "ext": f.suffix,
            }
            
            all_files.append(file_info)
            
            if mtime >= cutoff:
                recent.append(file_info)
                
        except Exception as e:
            continue
    
    # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
    recent.sort(key=lambda x: x["mtime"], reverse=True)
    all_files.sort(key=lambda x: x["mtime"], reverse=True)
    
    return recent, all_files


def build_report(recent, all_files, days=10):
    """ساخت گزارش"""
    lines = []
    
    lines.append("=" * 100)
    lines.append(f"  📊 گزارش فایل‌های جدید ({days} روز اخیر)")
    lines.append(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")
    
    # آمار
    lines.append(f"  📈 آمار کلی:")
    lines.append(f"     کل فایل‌ها (بدون skip): {len(all_files):,}")
    lines.append(f"     فایل‌های {days} روز اخیر: {len(recent):,}")
    lines.append("")
    
    # بر اساس پسوند
    lines.append(f"  📁 بر اساس پسوند:")
    ext_count = {}
    for f in recent:
        ext = f["ext"] or "بدون پسوند"
        ext_count[ext] = ext_count.get(ext, 0) + 1
    
    for ext, count in sorted(ext_count.items(), key=lambda x: -x[1]):
        lines.append(f"     {ext:15} → {count:4} فایل")
    lines.append("")
    
    # بر اساس پوشه
    lines.append(f"  📂 بر اساس پوشه:")
    dir_count = {}
    for f in recent:
        parent = str(Path(f["path"]).parent)
        if parent == ".":
            parent = "(ریشه)"
        dir_count[parent] = dir_count.get(parent, 0) + 1
    
    for d, count in sorted(dir_count.items(), key=lambda x: -x[1]):
        lines.append(f"     {d:30} → {count:4} فایل")
    lines.append("")
    
    lines.append("=" * 100)
    lines.append(f"  📝 لیست کامل فایل‌های {days} روز اخیر:")
    lines.append("=" * 100)
    lines.append("")
    
    # گروه‌بندی بر اساس تاریخ
    by_date = {}
    for f in recent:
        date_str = f["mtime"].strftime("%Y-%m-%d")
        if date_str not in by_date:
            by_date[date_str] = []
        by_date[date_str].append(f)
    
    for date_str in sorted(by_date.keys(), reverse=True):
        files = by_date[date_str]
        lines.append(f"\n📅 {date_str} ({len(files)} فایل)")
        lines.append("-" * 100)
        
        for f in files:
            time_str = f["mtime"].strftime("%H:%M:%S")
            size_str = f"{f['size']:>10,} b"
            lines.append(f"  [{time_str}] {size_str}  {f['path']}")
    
    lines.append("")
    lines.append("=" * 100)
    lines.append("  پایان گزارش")
    lines.append("=" * 100)
    
    return "\n".join(lines)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  🔍 شناسایی فایل‌های جدید ({DAYS} روز اخیر)")
    safe_print("=" * 80)
    safe_print("")
    
    safe_print("  📂 اسکن پروژه...")
    recent, all_files = get_recent_files(DAYS)
    
    safe_print(f"     ✅ کل: {len(all_files):,} فایل")
    safe_print(f"     ✅ جدید ({DAYS} روز): {len(recent):,} فایل")
    safe_print("")
    
    safe_print("  📝 ساخت گزارش...")
    report = build_report(recent, all_files, DAYS)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    
    safe_print(f"     ✅ ذخیره شد: {OUTPUT_FILE}")
    safe_print("")
    
    # خلاصه
    safe_print("=" * 80)
    safe_print(f"  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    
    # پسوندها
    ext_count = {}
    for f in recent:
        ext = f["ext"] or "بدون"
        ext_count[ext] = ext_count.get(ext, 0) + 1
    
    safe_print("  📁 پسوندها:")
    for ext, count in sorted(ext_count.items(), key=lambda x: -x[1])[:10]:
        safe_print(f"     {ext:15} → {count:4}")
    safe_print("")
    
    # پوشه‌ها
    dir_count = {}
    for f in recent:
        parent = str(Path(f["path"]).parent)
        if parent == ".":
            parent = "(ریشه)"
        dir_count[parent] = dir_count.get(parent, 0) + 1
    
    safe_print("  📂 پوشه‌ها:")
    for d, count in sorted(dir_count.items(), key=lambda x: -x[1])[:10]:
        safe_print(f"     {d:30} → {count:4}")
    safe_print("")
    
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
