# install_database.py
# فاز ۶: دیتابیس برای داده‌های حجیم
# اجرا: python install_database.py

import os
import sys
import sqlite3
import json
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
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
DB_FILE = DATA_DIR / "smart_bourse_v2.db"
HISTORY_DIR = DATA_DIR / "history"
BACKUP_DIR = PROJECT_ROOT / "backup" / "database"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def backup_history():
    """بکاپ از data/history"""
    if not HISTORY_DIR.exists():
        return None
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"history_backup_{timestamp}"
    
    shutil.copytree(HISTORY_DIR, backup_path)
    return backup_path


def create_database():
    """ساخت دیتابیس جدید"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    # جدول سهام
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol)
        )
    """)
    
    # جدول تاریخچه قیمت
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        )
    """)
    
    # جدول سیگنال‌ها
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            category TEXT,
            ratio REAL,
            rsi REAL,
            technical_score REAL,
            final_score REAL,
            last_price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول نتایج
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            category TEXT,
            price_at_signal REAL,
            price_after_1d REAL,
            price_after_3d REAL,
            price_after_7d REAL,
            success INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول معاملات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            action TEXT,
            price REAL,
            quantity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ایندکس‌ها
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_symbol ON price_history(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_date ON price_history(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_date ON signals(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome_date ON outcomes(date)")
    
    conn.commit()
    conn.close()
    
    return True


def migrate_history():
    """مهاجرت تاریخچه JSON به دیتابیس"""
    if not HISTORY_DIR.exists():
        return 0, 0
    
    json_files = list(HISTORY_DIR.glob("*_history.json"))
    
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    migrated = 0
    errors = 0
    
    for f in json_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            
            # استخراج نماد از اسم فایل
            symbol = f.stem.replace("_history", "")
            
            # اضافه کردن سهام
            cursor.execute(
                "INSERT OR IGNORE INTO stocks (symbol, name) VALUES (?, ?)",
                (symbol, symbol)
            )
            
            # اضافه کردن تاریخچه
            if isinstance(data, list):
                for item in data:
                    try:
                        date = item.get("date") or item.get("Date")
                        if not date:
                            continue
                        
                        cursor.execute("""
                            INSERT OR IGNORE INTO price_history 
                            (symbol, date, open, high, low, close, volume)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            symbol,
                            str(date),
                            item.get("open") or item.get("Open") or 0,
                            item.get("high") or item.get("High") or 0,
                            item.get("low") or item.get("Low") or 0,
                            item.get("close") or item.get("Close") or 0,
                            item.get("volume") or item.get("Volume") or 0,
                        ))
                    except Exception:
                        errors += 1
            
            migrated += 1
        except Exception:
            errors += 1
    
    conn.commit()
    conn.close()
    
    return migrated, errors


def migrate_signals():
    """مهاجرت سیگنال‌ها"""
    signals_file = DATA_DIR / "ai" / "memory.jsonl"
    outcomes_file = DATA_DIR / "ai" / "outcomes.jsonl"
    
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    signals_count = 0
    outcomes_count = 0
    
    # سیگنال‌ها
    if signals_file.exists():
        with open(signals_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    cursor.execute("""
                        INSERT INTO signals
                        (date, symbol, category, ratio, rsi, technical_score, final_score, last_price)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get("date"),
                        item.get("symbol"),
                        item.get("category"),
                        item.get("ratio"),
                        item.get("rsi"),
                        item.get("technical_score"),
                        item.get("final_score"),
                        item.get("last_price"),
                    ))
                    signals_count += 1
                except Exception:
                    pass
    
    # نتایج
    if outcomes_file.exists():
        with open(outcomes_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    cursor.execute("""
                        INSERT INTO outcomes
                        (date, symbol, category, price_at_signal, price_after_1d,
                         price_after_3d, price_after_7d, success)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get("date"),
                        item.get("symbol"),
                        item.get("category"),
                        item.get("price_at_signal"),
                        item.get("price_after_1d"),
                        item.get("price_after_3d"),
                        item.get("price_after_7d"),
                        1 if item.get("success") else 0,
                    ))
                    outcomes_count += 1
                except Exception:
                    pass
    
    conn.commit()
    conn.close()
    
    return signals_count, outcomes_count


def show_stats():
    """نمایش آمار دیتابیس"""
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
    safe_print("  🗄️ فاز ۶: دیتابیس")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بکاپ
    safe_print("  📦 بکاپ از history/...")
    backup = backup_history()
    if backup:
        safe_print(f"     ✅ {backup.name}")
    safe_print("")

    # ۲. ساخت دیتابیس
    safe_print("  🗄️ ساخت دیتابیس...")
    create_database()
    safe_print(f"     ✅ {DB_FILE.name}")
    safe_print("")

    # ۳. مهاجرت تاریخچه
    safe_print("  📂 مهاجرت تاریخچه JSON...")
    migrated, errors = migrate_history()
    safe_print(f"     ✅ {migrated} فایل مهاجرت شد")
    if errors > 0:
        safe_print(f"     ⚠️ {errors} خطا")
    safe_print("")

    # ۴. مهاجرت سیگنال‌ها
    safe_print("  📊 مهاجرت سیگنال‌ها...")
    signals, outcomes = migrate_signals()
    safe_print(f"     ✅ {signals} سیگنال")
    safe_print(f"     ✅ {outcomes} نتیجه")
    safe_print("")

    # ۵. آمار
    safe_print("  📊 آمار دیتابیس...")
    stats = show_stats()
    safe_print("")
    for table, count in stats.items():
        safe_print(f"     {table:<20} : {count:,}")
    safe_print("")

    # ۶. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print(f"  ✅ دیتابیس: {DB_FILE}")
    safe_print(f"  ✅ {migrated} فایل مهاجرت شد")
    safe_print(f"  ✅ {signals} سیگنال")
    safe_print(f"  ✅ {outcomes} نتیجه")
    if backup:
        safe_print(f"  📦 بکاپ: {backup.name}")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
