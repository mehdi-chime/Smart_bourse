# install_cleanup.py
# فاز ۳: پاکسازی — ادغام نسخه‌ها
# اجرا: python install_cleanup.py

import os
import sys
import shutil
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
BACKUP_DIR = PROJECT_ROOT / "backup" / "cleanup"
ARCHIVE_DIR = PROJECT_ROOT / "_archive"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def backup_files():
    """بکاپ از فایل‌های اضافی"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"cleanup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path


def archive_files(files, backup_path):
    """آرشیو فایل‌های اضافی"""
    archived = []
    
    for f in files:
        src = PROJECT_ROOT / f
        if not src.exists():
            continue
        
        # بکاپ
        dst_backup = backup_path / f
        dst_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst_backup)
        
        # آرشیو
        dst_archive = ARCHIVE_DIR / f
        dst_archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst_archive))
        
        archived.append(f)
    
    return archived


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🧹 فاز ۳: پاکسازی")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بکاپ
    safe_print("  📦 بکاپ...")
    backup_path = backup_files()
    safe_print(f"     ✅ {backup_path.name}")
    safe_print("")

    # ۲. فایل‌های اضافی (نسخه‌های قدیمی)
    files_to_archive = [
        # school_mode (نگه‌داشتن v7)
        "school_mode_v3.py",
        "school_mode_v5.py",
        
        # tomorrow (نگه‌داشتن tomorrow_picks_v2)
        "check_tomorrow.py",
        "tomorrow_picks.py",
        "tomorrow_v5.py",
        
        # smart_scanner (نگه‌داشتن v8)
        "smart_scanner_v5.py",
        
        # install_school (نگه‌داشتن v5)
        "install_school_v3.py",
        
        # اسم‌های عجیب
        "# golden_scanner.py",
        "golden_scanner.py",
        "engines/swing_target.py.py",
        
        # فایل‌های تکراری
        "list_files.py",
        "check_data.py",
        "daily_change.py",
        "filter_volume.py",
        "simple_signal.py",
        "show_stocks.py",
        "find_order_book.py",
        "custom_signal.py",
        "delete_symbols.py",
        "excel_to_json.py",
        "process_trades.py",
        "market.py",
        "market_manager.py",
        "market_scanner.py",
        "market_downloader.py",
        "order_book_parser.py",
        "save_order_book.py",
        "find_data.py",
        "view_structure.py",
        "run_downloader.py",
    ]

    safe_print("  🗂️ آرشیو فایل‌های اضافی...")
    safe_print("")

    archived = archive_files(files_to_archive, backup_path)
    
    for f in archived:
        safe_print(f"     ✅ {f}")
    safe_print("")

    # ۳. پوشه‌های اضافی
    dirs_to_archive = [
        "python ba claude",
        "backup",
    ]

    safe_print("  📁 آرشیو پوشه‌ها...")
    safe_print("")

    for d in dirs_to_archive:
        src = PROJECT_ROOT / d
        if not src.exists():
            continue
        if d == "backup":
            continue  # بکاپ رو نگه دار
        
        dst = ARCHIVE_DIR / d
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        safe_print(f"     ✅ {d}/")
    safe_print("")

    # ۴. آمار
    safe_print("  📊 آمار...")
    py_files = list(PROJECT_ROOT.rglob("*.py"))
    py_files = [f for f in py_files if "_archive" not in str(f) and "backup" not in str(f)]
    all_files = [f for f in PROJECT_ROOT.rglob("*") if f.is_file() and "_archive" not in str(f) and "backup" not in str(f)]
    
    safe_print(f"     فایل‌های py: {len(py_files)}")
    safe_print(f"     کل فایل‌ها: {len(all_files)}")
    safe_print(f"     آرشیو شده: {len(archived)}")
    safe_print("")

    # ۵. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print(f"  ✅ {len(archived)} فایل آرشیو شد")
    safe_print(f"  ✅ {len(dirs_to_archive)} پوشه آرشیو شد")
    safe_print(f"  📁 فایل‌های py باقی‌مانده: {len(py_files)}")
    safe_print(f"  📦 بکاپ: {backup_path}")
    safe_print(f"  🗂️ آرشیو: {ARCHIVE_DIR}")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
