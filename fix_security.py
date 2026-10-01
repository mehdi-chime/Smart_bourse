# fix_security.py
# پاکسازی امنیتی + آپدیت .gitignore
# اجرا: python fix_security.py

import os
import sys
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
GITIGNORE = PROJECT_ROOT / ".gitignore"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔒 پاکسازی امنیتی")
    safe_print("=" * 80)
    safe_print("")

    # ۱. پاک کردن فایل‌های .bak
    safe_print("  🗑️ پاک کردن فایل‌های .bak...")
    
    bak_files = list(PROJECT_ROOT.rglob("*.bak"))
    if not bak_files:
        safe_print("     ℹ️ فایل .bak پیدا نشد")
    else:
        for f in bak_files:
            try:
                f.unlink()
                safe_print(f"     ✅ {f.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                safe_print(f"     ❌ {f.name}: {e}")
    safe_print("")

    # ۲. آپدیت .gitignore
    safe_print("  📝 آپدیت .gitignore...")
    
    if not GITIGNORE.exists():
        safe_print("     ⚠️ .gitignore نیست، ساخته می‌شه...")
        GITIGNORE.write_text("", encoding="utf-8")
    
    content = GITIGNORE.read_text(encoding="utf-8")
    
    additions = [
        "",
        "# ═══════════════════════════════════════════════════════",
        "# 🔒 BACKUP FILES",
        "# ═══════════════════════════════════════════════════════",
        "*.bak",
        "*.backup",
        "*.old",
        "*~",
        "alert_config*.bak",
        "alert_config*.backup",
    ]
    
    if "*.bak" not in content:
        content += "\n".join(additions)
        GITIGNORE.write_text(content, encoding="utf-8")
        safe_print("     ✅ .bak اضافه شد")
    else:
        safe_print("     ℹ️ .bak از قبل هست")
    safe_print("")

    # ۳. چک نهایی
    safe_print("  🔍 چک git status...")
    import subprocess
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
        errors="ignore",
    )
    
    if result and result.stdout:
        lines = result.stdout.strip().split("\n")
        
        # چک alert_config
        danger = False
        for line in lines:
            if "alert_config" in line and "example" not in line:
                safe_print(f"     🚨 خطر: {line}")
                danger = True
        
        if not danger:
            safe_print(f"     ✅ {len(lines)} فایل (امن)")
            
            # نمایش چند تا
            for line in lines[:8]:
                safe_print(f"        {line}")
    else:
        safe_print("     ℹ️ چیزی برای commit نیست")
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ فایل‌های .bak پاک شدن")
    safe_print("  ✅ .gitignore آپدیت شد")
    safe_print("  ✅ چک امنیت انجام شد")
    safe_print("")
    safe_print("  🎯 قدم بعدی:")
    safe_print("     python auto_github.py")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
