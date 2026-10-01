# cleanup_project.py
# پاکسازی و منظم کردن Smart_Bourse
# ⚠️ این اسکریپت فایل‌ها رو حذف/منتقل می‌کنه
# اول پشتیبان بگیر: python cleanup_project.py --backup

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
BACKUP_DIR = ROOT.parent / f"smart_bourse_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"


def backup():
    """پشتیبان‌گیری"""
    print("=" * 80)
    print("  📦 پشتیبان‌گیری")
    print("=" * 80)

    if BACKUP_DIR.exists():
        print(f"  ⚠️ پشتیبان موجوده: {BACKUP_DIR}")
        return True

    try:
        shutil.copytree(ROOT, BACKUP_DIR, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.git', 'venv', '.venv', 'data'
        ))
        print(f"  ✅ پشتیبان: {BACKUP_DIR}")
        return True
    except Exception as e:
        print(f"  ❌ خطا: {e}")
        return False


def find_empty_files():
    """فایل‌های خالی"""
    empty = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {'__pycache__', '.git'}]
        for f in filenames:
            if f.endswith('.py'):
                full = Path(dirpath) / f
                if full.stat().st_size < 50:
                    empty.append(str(full.relative_to(ROOT)))
    return empty


def find_duplicates():
    """فایل‌های تکراری"""
    from collections import defaultdict

    names = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {'__pycache__', '.git'}]
        for f in filenames:
            if f.endswith('.py'):
                full = Path(dirpath) / f
                names[f].append(str(full.relative_to(ROOT)))

    return {name: paths for name, paths in names.items() if len(paths) > 1}


def find_root_files():
    """فایل‌های ریشه"""
    root_files = []
    for f in ROOT.glob('*.py'):
        root_files.append(f.name)
    return root_files


def categorize_root_files():
    """دسته‌بندی فایل‌های ریشه"""
    categories = {
        "main": ["main.py", "run.py", "daily_runner.py"],
        "install": ["install.py", "install_scheduler.py"],
        "config": ["config.py", "project_config.py"],
        "hunter": ["opportunity_hunter_v54.py", "analyze_top_signals.py", "analyze_foolad_khegostar.py"],
        "check": ["check_data.py", "check_data_date.py", "check_db.py", "check_history.py",
                  "check_project.py", "check_stock_data.py"],
        "find": ["find_basing_relative.py", "find_basing_stocks.py", "find_basing_stocks_advanced.py",
                 "find_data.py", "find_high_buyer_ratio.py", "find_high_buyer_ratio_weekly.py",
                 "find_order_book.py"],
        "tsetmc": ["tsetmc_all_symbols.py", "tsetmc_auto.py", "tsetmc_fetcher.py",
                   "tsetmc_order.py", "tsetmc_selenium.py"],
        "show": ["show_db.py", "show_stocks.py", "list_files.py", "view_structure.py"],
        "sync": ["auto_push.py", "chatgpt_bridge.py", "send_diagnostic_to_github.py",
                 "sync_for_ai.py", "sync_missing_python_to_github.py", "update_project.py",
                 "update_roadmap.py"],
        "test": ["test.khegostar.py", "test_api.py", "test_csv.py", "test_database.py",
                 "test_eitaa.py", "test_foolad.py"],
        "backtest": ["batch_backtest.py"],
        "misc": ["bidar_scraper.py", "custom_signal.py", "daily_change.py",
                 "delete_symbols.py", "download_all_history.py", "edu_showcase.py",
                 "excel_to_json.py", "filter_volume.py", "full_scanner.py",
                 "install_edu.py", "make_edu.py", "market.py", "market_downloader.py",
                 "market_manager.py", "market_scanner.py", "order_book_parser.py",
                 "process_trades.py", "run_downloader.py", "save_order_book.py",
                 "simple_signal.py", "update_khegostar.py"],
    }
    return categories


def generate_cleanup_plan():
    """تولید نقشه پاکسازی"""
    print()
    print("=" * 80)
    print("  📋 نقشه پاکسازی")
    print("=" * 80)
    print()

    # ۱. فایل‌های خالی
    empty = find_empty_files()
    print(f"  🗑️ فایل‌های خالی (پیشنهاد حذف): {len(empty)}")
    for e in empty[:20]:
        print(f"      {e}")
    if len(empty) > 20:
        print(f"      ... و {len(empty) - 20} مورد دیگر")
    print()

    # ۲. تکراری‌ها
    dups = find_duplicates()
    print(f"  🔴 فایل‌های تکراری: {len(dups)}")
    for name, paths in sorted(dups.items()):
        print(f"      🔴 {name}:")
        for p in paths:
            print(f"          {p}")
    print()

    # ۳. فایل‌های ریشه
    root_files = find_root_files()
    print(f"  📁 فایل‌های ریشه: {len(root_files)}")

    categories = categorize_root_files()
    categorized = set()
    for cat, files in categories.items():
        for f in files:
            categorized.add(f)

    uncategorized = [f for f in root_files if f not in categorized]
    print(f"      ✅ دسته‌بندی شده: {len(categorized)}")
    print(f"      ⚠️ دسته‌بندی نشده: {len(uncategorized)}")
    for f in uncategorized[:10]:
        print(f"          {f}")
    print()

    return empty, dups, root_files, categories


def apply_cleanup(empty, dups, root_files, categories):
    """اعمال پاکسازی"""
    print()
    print("=" * 80)
    print("  🚀 اعمال پاکسازی")
    print("=" * 80)
    print()

    # ۱. حذف فایل‌های خالی
    print("  🗑️ حذف فایل‌های خالی...")
    for e in empty:
        try:
            (ROOT / e).unlink()
            print(f"      ✅ حذف: {e}")
        except Exception as ex:
            print(f"      ❌ خطا در {e}: {ex}")

    # ۲. ساخت پوشه scripts
    scripts_dir = ROOT / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    print(f"  📁 ساخت: scripts/")

    # ۳. انتقال فایل‌های ریشه به scripts
    for cat, files in categories.items():
        if cat in ["main", "install", "config", "hunter"]:
            continue  # اینا تو ریشه بمونن

        cat_dir = scripts_dir / cat
        cat_dir.mkdir(exist_ok=True)

        for f in files:
            src = ROOT / f
            if src.exists():
                dst = cat_dir / f
                try:
                    shutil.move(str(src), str(dst))
                    print(f"      ✅ {f} → scripts/{cat}/")
                except Exception as ex:
                    print(f"      ❌ خطا در {f}: {ex}")

    print()
    print("  ✅ پاکسازی تمام شد!")


def main():
    print()
    print("=" * 80)
    print("  🧹 SMART_BOURSE CLEANUP")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # پشتیبان
    if not backup():
        print("  ❌ پشتیبان‌گیری نشد. خروج.")
        return

    # نقشه
    empty, dups, root_files, categories = generate_cleanup_plan()

    # تأیید
    print("=" * 80)
    print(f"  ⚠️ آیا مطمئنی؟ (پشتیبان گرفته شد)")
    print(f"     - حذف {len(empty)} فایل خالی")
    print(f"     - انتقال {len(root_files)} فایل ریشه به scripts/")
    print("=" * 80)
    answer = input("  بنویس 'YES' برای ادامه: ")

    if answer.strip() != "YES":
        print("  ❌ لغو شد.")
        return

    # اعمال
    apply_cleanup(empty, dups, root_files, categories)

    print()
    print("=" * 80)
    print("  ✅ تمام شد!")
    print(f"  📦 پشتیبان: {BACKUP_DIR}")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
