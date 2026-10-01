# fix_database.py
# اصلاح مهاجرت دیتابیس
# اجرا: python fix_database.py

import os
import sys
import sqlite3
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
DB_FILE = PROJECT_ROOT / "data" / "smart_bourse_v2.db"
HISTORY_DIR = PROJECT_ROOT / "data" / "history"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def migrate_prices():
    """مهاجرت قیمت‌ها با کلیدهای درست"""
    if not HISTORY_DIR.exists():
        return 0, 0, 0
    
    json_files = list(HISTORY_DIR.glob("*_history.json"))
    
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    migrated = 0
    rows = 0
    errors = 0
    
    for f in json_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            
            if not isinstance(data, list):
                continue
            
            # استخراج نماد از اسم فایل
            symbol = f.stem.replace("_history", "")
            
            # اضافه کردن سهام
            cursor.execute(
                "INSERT OR IGNORE INTO stocks (symbol, name) VALUES (?, ?)",
                (symbol, symbol)
            )
            
            # اضافه کردن قیمت‌ها
            for item in data:
                try:
                    trade_date = str(item.get("trade_date", ""))
                    if not trade_date:
                        continue
                    
                    # فرمت تاریخ: 20260831 → 2026-08-31
                    if len(trade_date) == 8:
                        date_str = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
                    else:
                        date_str = trade_date
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO price_history 
                        (symbol, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        date_str,
                        item.get("open_price", 0),
                        item.get("high_price", 0),
                        item.get("low_price", 0),
                        item.get("close_price", 0),
                        int(item.get("volume", 0)),
                    ))
                    rows += 1
                except Exception:
                    errors += 1
            
            migrated += 1
        except Exception:
            errors += 1
    
    conn.commit()
    conn.close()
    
    return migrated, rows, errors


def show_stats():
    """آمار"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    stats = {}
    for table in ["stocks", "price_history", "signals", "outcomes", "trades"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    
    conn.close()
    return stats


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔧 اصلاح مهاجرت دیتابیس")
    safe_print("=" * 80)
    safe_print("")

    # ۱. پاک کردن price_history
    safe_print("  🗑️ پاک کردن price_history قدیمی...")
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM price_history")
    conn.commit()
    conn.close()
    safe_print("     ✅ پاک شد")
    safe_print("")

    # ۲. مهاجرت
    safe_print("  📂 مهاجرت قیمت‌ها با کلیدهای درست...")
    migrated, rows, errors = migrate_prices()
    safe_print(f"     ✅ {migrated} فایل")
    safe_print(f"     ✅ {rows:,} رکورد")
    if errors > 0:
        safe_print(f"     ⚠️ {errors} خطا")
    safe_print("")

    # ۳. آمار
    safe_print("  📊 آمار دیتابیس...")
    stats = show_stats()
    safe_print("")
    for table, count in stats.items():
        safe_print(f"     {table:<20} : {count:,}")
    safe_print("")

    # ۴. تست
    safe_print("  🧪 تست نمونه...")
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM price_history LIMIT 3")
    for row in cursor.fetchall():
        safe_print(f"     {row}")
    conn.close()
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
