# install_github_safe.py
# آماده‌سازی GitHub بدون توکن
# اجرا: python install_github_safe.py

import os
import sys
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


# ═══════════════════════════════════════════════════════════
# .gitignore
# ═══════════════════════════════════════════════════════════

GITIGNORE_LINES = [
    "# ═══════════════════════════════════════════════════════",
    "# 🔒 SECRETS - NEVER COMMIT!",
    "# ═══════════════════════════════════════════════════════",
    "scanner/alert_config.py",
    "**/alert_config.py",
    "**/config_secret.py",
    "*.key",
    "*.pem",
    ".env",
    "",
    "# ═══════════════════════════════════════════════════════",
    "# 📊 DATA - Large files",
    "# ═══════════════════════════════════════════════════════",
    "data/history/",
    "data/real_flow/",
    "data/live_records/",
    "data/ai/*.pkl",
    "data/ai/*.jsonl",
    "data/*.db",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "",
    "# ═══════════════════════════════════════════════════════",
    "# 📦 BACKUPS",
    "# ═══════════════════════════════════════════════════════",
    "backup/",
    "_archive/",
    "_for_deepseek/",
    "_for_chat/",
    "*.zip",
    "*.tar.gz",
    "",
    "# ═══════════════════════════════════════════════════════",
    "# 📝 LOGS",
    "# ═══════════════════════════════════════════════════════",
    "logs/",
    "*.log",
    "",
    "# ═══════════════════════════════════════════════════════",
    "# 🐍 PYTHON",
    "# ═══════════════════════════════════════════════════════",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    "",
    "# ═══════════════════════════════════════════════════════",
    "# 💻 IDE",
    "# ═══════════════════════════════════════════════════════",
    ".idea/",
    ".vscode/",
    "*.swp",
    "*.swo",
    "",
    "# ═══════════════════════════════════════════════════════",
    "# 🖥️ OS",
    "# ═══════════════════════════════════════════════════════",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "",
    "# ═══════════════════════════════════════════════════════",
    "# 📊 REPORTS",
    "# ═══════════════════════════════════════════════════════",
    "reports/dashboard*.html",
    "reports/backtest*.json",
    "reports/*.txt",
    "",
]


# ═══════════════════════════════════════════════════════════
# alert_config.example.py
# ═══════════════════════════════════════════════════════════

ALERT_CONFIG_EXAMPLE_LINES = [
    "# ═══════════════════════════════════════════════════════════",
    "# Smart_Bourse - Alert Configuration (EXAMPLE)",
    "# ═══════════════════════════════════════════════════════════",
    "# این فایل نمونه است. فایل اصلی رو خودت بساز:",
    "# scanner/alert_config.py",
    "# ═══════════════════════════════════════════════════════════",
    "",
    "# توکن ایتایار (از پنل eitaayar.ir)",
    'EITAA_TOKEN = "YOUR_TOKEN_HERE"',
    "",
    "# شناسه کانال (Chat ID)",
    'EITAA_CHAT_ID = "YOUR_CHAT_ID_HERE"',
    "",
    "# ═══════════════════════════════════════════════════════════",
    "# سهم‌های تحت نظر",
    "# ═══════════════════════════════════════════════════════════",
    "WATCH_SYMBOLS = [",
    '    {"name": "تابان",   "aliases": ["تابان"]},',
    '    {"name": "پکویر",   "aliases": ["پكوير", "پکویر"]},',
    '    {"name": "سمهریز",  "aliases": ["سهرمز", "سمهریز"]},',
    '    {"name": "احیا",    "aliases": ["احیا", "احياء"]},',
    '    {"name": "پیزد",    "aliases": ["پیزد"]},',
    '    {"name": "خپارس",   "aliases": ["خپارس"]},',
    '    {"name": "خگستر",   "aliases": ["خگستر"]},',
    '    {"name": "فولاد",   "aliases": ["فولاد"]},',
    "]",
    "",
    "# ═══════════════════════════════════════════════════════════",
    "# تنظیمات هشدار",
    "# ═══════════════════════════════════════════════════════════",
    "CHECK_INTERVAL = 30",
    "STRONG_BUY_RATIO = 5.0",
    "STRONG_SELL_RATIO = 0.2",
    "ALERT_ON_QUEUE = True",
    "ALERT_ON_STRONG = True",
    "ALERT_ON_BIG_CHANGE = True",
    "BIG_CHANGE_PCT = 3.0",
    "",
    "# ═══════════════════════════════════════════════════════════",
    "# ساعت‌های فعال",
    "# ═══════════════════════════════════════════════════════════",
    "MARKET_OPEN_HOUR = 9",
    "MARKET_CLOSE_HOUR = 12",
    "MARKET_CLOSE_MINUTE = 30",
]


def write_file(path, lines):
    content = "\n".join(lines)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def check_gitignore():
    """چک .gitignore"""
    gitignore = PROJECT_ROOT / ".gitignore"
    
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        
        # چک alert_config
        if "alert_config.py" in content:
            safe_print("     ✅ alert_config.py در .gitignore هست")
        else:
            safe_print("     ⚠️ alert_config.py در .gitignore نیست!")
    
    return True


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔒 آماده‌سازی GitHub (بدون توکن)")
    safe_print("=" * 80)
    safe_print("")

    # ۱. .gitignore
    safe_print("  📄 ساخت .gitignore...")
    size = write_file(PROJECT_ROOT / ".gitignore", GITIGNORE_LINES)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۲. alert_config.example.py
    safe_print("  📄 ساخت scanner/alert_config.example.py...")
    size = write_file(PROJECT_ROOT / "scanner" / "alert_config.example.py", ALERT_CONFIG_EXAMPLE_LINES)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۳. چک امنیت
    safe_print("  🔍 چک امنیت...")
    check_gitignore()
    safe_print("")

    # ۴. چک alert_config اصلی
    safe_print("  🔍 چک alert_config.py...")
    alert_file = PROJECT_ROOT / "scanner" / "alert_config.py"
    if alert_file.exists():
        content = alert_file.read_text(encoding="utf-8")
        if "bot502704" in content or "b4916751" in content:
            safe_print("     ⚠️ توکن واقعی در alert_config.py هست!")
            safe_print("     ✅ ولی در .gitignore هست (به GitHub نمی‌ره)")
    safe_print("")

    # ۵. دستورات Git
    safe_print("=" * 80)
    safe_print("  📋 دستورات Git")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  1️⃣  چک .gitignore:")
    safe_print("     git status")
    safe_print("")
    safe_print("  2️⃣  اضافه کردن فایل‌ها:")
    safe_print("     git add .")
    safe_print("")
    safe_print("  3️⃣  چک اینکه alert_config.py نباشه:")
    safe_print("     git status | findstr alert_config")
    safe_print("     (نباید چیزی نشون بده)")
    safe_print("")
    safe_print("  4️⃣  Commit:")
    safe_print('     git commit -m "v5.0 — AI + ML + Database + 12 phases"')
    safe_print("")
    safe_print("  5️⃣  Push:")
    safe_print("     git push origin main")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
