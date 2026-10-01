# collect_files.py
# جمع‌آوری فایل‌های مهم پروژه
# اجرا: python collect_files.py

import os
import sys
import shutil
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
OUTPUT_DIR = PROJECT_ROOT / "_for_deepseek"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def should_skip(path):
    """فایل‌هایی که نباید کپی بشن"""
    skip_patterns = [
        "__pycache__", ".git", ".idea", ".vscode",
        "backup", "data/history", "node_modules",
        ".pyc", ".log",  # لاگ‌ها رو جدا می‌فرستیم
    ]
    path_str = str(path).lower()
    for pattern in skip_patterns:
        if pattern.lower() in path_str:
            return True
    return False


def collect_files():
    """جمع‌آوری فایل‌های مهم"""
    
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ═══════════════════════════════════════════════════════
    # لیست فایل‌های مهم
    # ═══════════════════════════════════════════════════════
    
    important_files = [
        # فایل‌های ریشه
        "main.py",
        "config.py",
        "project_config.py",
        "daily_runner.py",
        "auto_trader.py",
        "requirements.txt",
        "README.md",
        "smart_scanner_v5.py",
        "smart_scanner_v8.py",
        "smart_bourse_v10.py",
        "school_mode_v3.py",
        "school_mode_v5.py",
        "school_mode_v7.py",
        "tomorrow_picks.py",
        "tomorrow_picks_v2.py",
        "tomorrow_v5.py",
        "check_tomorrow.py",
        "night_check.py",
        "golden_scanner.py",
        "install_school_v3.py",
        "install_school_v5.py",
        "# golden_scanner.py",
        
        # scanner
        "scanner/alert_config.py",
        
        # logs (آخرین)
        "logs/school_v7.log",
        "logs/auto_runner_2026-10-01.log",
        "logs/auto_runner_2026-09-30.log",
        
        # نقشه‌راه‌ها
        "Smart_Bourse_RoadMap.txt",
        "DeepSeek_RoadMap.txt",
    ]

    # ═══════════════════════════════════════════════════════
    # پوشه‌های مهم (همه فایل‌های py)
    # ═══════════════════════════════════════════════════════
    
    important_dirs = [
        "ai",
        "analysis",
        "backtest",
        "core",
        "decision",
        "engines",
        "eitaa",
        "fundamental",
        "history",
        "indicators",
        "market",
        "models",
        "monitors",
        "news",
        "paper",
        "portfolio",
        "reports",
        "risk",
        "scheduler",
        "scanner",
        "strategy",
        "ui",
        "utils",
        "database",
        "charts",
        "python ba claude",
        "scripts",  # فقط لیست، نه محتوا
    ]

    collected = []
    skipped = []

    # کپی فایل‌های مهم
    safe_print("  📄 کپی فایل‌های مهم...")
    for rel_path in important_files:
        src = PROJECT_ROOT / rel_path
        if src.exists():
            dst = OUTPUT_DIR / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src, dst)
                collected.append(rel_path)
                safe_print(f"     ✅ {rel_path}")
            except Exception as e:
                safe_print(f"     ❌ {rel_path}: {e}")
        else:
            safe_print(f"     ⚠️ {rel_path} (نیست)")

    safe_print("")

    # کپی پوشه‌ها (فقط py)
    safe_print("  📁 کپی پوشه‌ها (فقط .py)...")
    for dir_name in important_dirs:
        src_dir = PROJECT_ROOT / dir_name
        if not src_dir.exists():
            safe_print(f"     ⚠️ {dir_name}/ (نیست)")
            continue

        count = 0
        for py_file in src_dir.rglob("*.py"):
            if should_skip(py_file):
                continue
            
            rel = py_file.relative_to(PROJECT_ROOT)
            dst = OUTPUT_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.copy2(py_file, dst)
                collected.append(str(rel))
                count += 1
            except:
                pass

        safe_print(f"     ✅ {dir_name}/ ({count} فایل py)")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # لیست فایل‌های scripts (فقط اسم، نه محتوا)
    # ═══════════════════════════════════════════════════════
    
    safe_print("  📋 لیست فایل‌های scripts/...")
    scripts_dir = PROJECT_ROOT / "scripts"
    if scripts_dir.exists():
        scripts_list = []
        for py_file in scripts_dir.rglob("*.py"):
            scripts_list.append(str(py_file.relative_to(PROJECT_ROOT)))
        
        list_file = OUTPUT_DIR / "SCRIPTS_LIST.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            f.write(f"# لیست فایل‌های scripts/\n")
            f.write(f"# تعداد: {len(scripts_list)}\n\n")
            for s in sorted(scripts_list):
                f.write(f"{s}\n")
        
        safe_print(f"     ✅ {len(scripts_list)} فایل در SCRIPTS_LIST.txt")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # لیست همه فایل‌های py
    # ═══════════════════════════════════════════════════════
    
    safe_print("  📋 لیست همه فایل‌های py...")
    all_py = []
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if should_skip(py_file):
            continue
        all_py.append(str(py_file.relative_to(PROJECT_ROOT)))
    
    list_file = OUTPUT_DIR / "ALL_PY_FILES.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"# همه فایل‌های پایتون پروژه\n")
        f.write(f"# تعداد: {len(all_py)}\n\n")
        for s in sorted(all_py):
            f.write(f"{s}\n")
    
    safe_print(f"     ✅ {len(all_py)} فایل در ALL_PY_FILES.txt")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # لیست همه فایل‌ها
    # ═══════════════════════════════════════════════════════
    
    safe_print("  📋 لیست همه فایل‌ها...")
    all_files = []
    for f in PROJECT_ROOT.rglob("*"):
        if f.is_file() and not should_skip(f):
            all_files.append(str(f.relative_to(PROJECT_ROOT)))
    
    list_file = OUTPUT_DIR / "ALL_FILES.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"# همه فایل‌های پروژه\n")
        f.write(f"# تعداد: {len(all_files)}\n\n")
        for s in sorted(all_files):
            f.write(f"{s}\n")
    
    safe_print(f"     ✅ {len(all_files)} فایل در ALL_FILES.txt")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # لیست پوشه‌ها
    # ═══════════════════════════════════════════════════════
    
    safe_print("  📋 لیست پوشه‌ها...")
    dirs_list = []
    for d in PROJECT_ROOT.rglob("*"):
        if d.is_dir() and not should_skip(d):
            dirs_list.append(str(d.relative_to(PROJECT_ROOT)))
    
    list_file = OUTPUT_DIR / "ALL_DIRS.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"# همه پوشه‌های پروژه\n")
        f.write(f"# تعداد: {len(dirs_list)}\n\n")
        for s in sorted(dirs_list):
            f.write(f"{s}\n")
    
    safe_print(f"     ✅ {len(dirs_list)} پوشه در ALL_DIRS.txt")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # خلاصه
    # ═══════════════════════════════════════════════════════
    
    summary_file = OUTPUT_DIR / "SUMMARY.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  خلاصه‌ی جمع‌آوری فایل‌ها\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"پروژه: {PROJECT_ROOT}\n")
        f.write(f"خروجی: {OUTPUT_DIR}\n\n")
        f.write(f"تعداد فایل‌های کپی‌شده: {len(collected)}\n")
        f.write(f"تعداد فایل‌های py: {len(all_py)}\n")
        f.write(f"تعداد کل فایل‌ها: {len(all_files)}\n")
        f.write(f"تعداد پوشه‌ها: {len(dirs_list)}\n\n")
        f.write("=" * 80 + "\n")
        f.write("  فایل‌های کپی‌شده:\n")
        f.write("=" * 80 + "\n\n")
        for c in sorted(collected):
            f.write(f"  {c}\n")

    safe_print("=" * 80)
    safe_print(f"  ✅ تمام!")
    safe_print(f"  📁 خروجی: {OUTPUT_DIR}")
    safe_print(f"  📊 {len(collected)} فایل کپی شد")
    safe_print("=" * 80)
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ساخت ZIP
    # ═══════════════════════════════════════════════════════
    
    safe_print("  📦 ساخت ZIP...")
    zip_name = PROJECT_ROOT / f"for_deepseek_{datetime.now().strftime('%Y%m%d_%H%M')}"
    shutil.make_archive(str(zip_name), 'zip', str(OUTPUT_DIR))
    
    safe_print(f"  ✅ ZIP ساخته شد: {zip_name}.zip")
    safe_print("")


if __name__ == "__main__":
    collect_files()
