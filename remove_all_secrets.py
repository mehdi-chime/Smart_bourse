# remove_all_secrets.py
# پاک کردن همه فایل‌های حساس از GitHub
# اجرا: python remove_all_secrets.py

import os
import sys
import subprocess
import re
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
GITIGNORE_FILE = PROJECT_ROOT / ".gitignore"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def run_git(args):
    return subprocess.run(
        ["git"] + args,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )


def find_secrets():
    """پیدا کردن فایل‌های حساس"""
    safe_print("")
    safe_print("  🔍 پیدا کردن فایل‌های حساس...")
    safe_print("")

    # الگوهای توکن
    patterns = [
        (r'gsk_[A-Za-z0-9]{20,}', "Groq"),
        (r'sk-[A-Za-z0-9]{20,}', "DeepSeek/OpenAI"),
        (r'bot\d+:[A-Za-z0-9_-]{30,}', "Eitaa/Telegram"),
        (r'EITAA_TOKEN\s*=\s*["\']bot[^"\']+["\']', "Eitaa"),
        (r'API_KEY\s*=\s*["\'][^"\']{20,}["\']', "API Key"),
        (r'TOKEN\s*=\s*["\'][^"\']{20,}["\']', "Token"),
        (r'SECRET\s*=\s*["\'][^"\']{20,}["\']', "Secret"),
        (r'PASSWORD\s*=\s*["\'][^"\']+["\']', "Password"),
    ]

    # فایل‌های مهم
    files_to_check = [
        "config/llm_config.py",
        "scanner/alert_config.py",
        "config/__init__.py",
        "setup_groq.py",
        "setup_deepseek.py",
        "test_groq.py",
        "test_groq_v2.py",
        "test_groq_proxy.py",
        "ai/llm_analyzer.py",
        "finalize_project.py",
    ]

    # اضافه کردن همه py files
    for f in PROJECT_ROOT.rglob("*.py"):
        if "_archive" in str(f) or "backup" in str(f) or "__pycache__" in str(f):
            continue
        rel = str(f.relative_to(PROJECT_ROOT))
        if rel not in files_to_check:
            files_to_check.append(rel)

    found_files = []

    for rel in files_to_check:
        path = PROJECT_ROOT / rel
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")

            for pattern, name in patterns:
                if re.search(pattern, content):
                    found_files.append({
                        "path": rel,
                        "type": name,
                    })
                    break

        except:
            continue

    return found_files


def update_gitignore():
    """آپدیت .gitignore"""
    safe_print("")
    safe_print("  📝 آپدیت .gitignore...")

    # الگوهای امنیتی
    security_patterns = [
        "",
        "# ═══════════════════════════════════════════════════════",
        "# 🔒 SECRETS - NEVER COMMIT!",
        "# ═══════════════════════════════════════════════════════",
        "scanner/alert_config.py",
        "**/alert_config.py",
        "**/config_secret.py",
        "config/llm_config.py",
        "**/llm_config.py",
        "**/setup_groq.py",
        "**/setup_deepseek.py",
        "*.key",
        "*.pem",
        ".env",
        ".env.*",
        "",
        "# ═══════════════════════════════════════════════════════",
        "# 🔒 BACKUPS",
        "# ═══════════════════════════════════════════════════════",
        "*.bak",
        "*.backup",
        "*.old",
        "*~",
        "",
    ]

    if GITIGNORE_FILE.exists():
        content = GITIGNORE_FILE.read_text(encoding="utf-8")
    else:
        content = ""

    # اضافه کردن الگوهای جدید
    added = 0
    for pattern in security_patterns:
        if pattern and pattern not in content:
            content += "\n" + pattern
            added += 1

    GITIGNORE_FILE.write_text(content, encoding="utf-8")
    safe_print(f"     ✅ {added} الگو اضافه شد")


def remove_from_git(files):
    """پاک کردن فایل‌ها از Git"""
    safe_print("")
    safe_print("  🗑️ پاک کردن از Git...")

    for f in files:
        path = f["path"]
        safe_print(f"     🗑️ {path} ({f['type']})")

        result = run_git(["rm", "--cached", path])

        if result.returncode == 0:
            safe_print(f"        ✅ پاک شد")
        else:
            safe_print(f"        ⚠️ {result.stderr[:100]}")


def clean_tokens():
    """پاک کردن توکن‌ها از فایل‌ها"""
    safe_print("")
    safe_print("  🧹 پاک کردن توکن‌ها از فایل‌ها...")

    config_file = PROJECT_ROOT / "config" / "llm_config.py"

    if config_file.exists():
        content = config_file.read_text(encoding="utf-8")

        # پاک کردن Groq
        content = re.sub(
            r'GROQ_API_KEY\s*=\s*["\']gsk_[^"\']+["\']',
            'GROQ_API_KEY = ""',
            content
        )

        # پاک کردن DeepSeek
        content = re.sub(
            r'DEEPSEEK_API_KEY\s*=\s*["\']sk-[^"\']+["\']',
            'DEEPSEEK_API_KEY = ""',
            content
        )

        config_file.write_text(content, encoding="utf-8")
        safe_print("     ✅ llm_config.py پاک شد")

    # alert_config
    alert_file = PROJECT_ROOT / "scanner" / "alert_config.py"

    if alert_file.exists():
        content = alert_file.read_text(encoding="utf-8")

        content = re.sub(
            r'EITAA_TOKEN\s*=\s*["\']bot[^"\']+["\']',
            'EITAA_TOKEN = "YOUR_EITAA_TOKEN_HERE"',
            content
        )

        alert_file.write_text(content, encoding="utf-8")
        safe_print("     ✅ alert_config.py پاک شد")


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔒 پاک کردن فایل‌های حساس")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # ۱. پیدا کردن
    secrets = find_secrets()

    if not secrets:
        safe_print("  ✅ هیچ فایل حساسی پیدا نشد!")
    else:
        safe_print(f"  ⚠️ {len(secrets)} فایل حساس پیدا شد:")
        safe_print("")
        for s in secrets:
            safe_print(f"     🔴 {s['path']} ({s['type']})")

    safe_print("")

    # ۲. آپدیت .gitignore
    update_gitignore()

    # ۳. پاک کردن توکن‌ها
    clean_tokens()

    # ۴. پاک کردن از Git
    if secrets:
        remove_from_git(secrets)

    # ۵. commit و push
    safe_print("")
    safe_print("  💾 Commit و Push...")

    result = run_git(["add", ".gitignore"])
    safe_print(f"     git add .gitignore: {result.returncode}")

    result = run_git(["commit", "-m", "Remove all secrets from git"])
    if result.returncode == 0:
        safe_print("     ✅ Commit شد")
    else:
        safe_print(f"     ⚠️ {result.stdout[:100]}")

    # ۶. خلاصه
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print(f"  ✅ {len(secrets)} فایل حساس پیدا شد")
    safe_print("  ✅ .gitignore آپدیت شد")
    safe_print("  ✅ توکن‌ها پاک شدن")
    safe_print("  ✅ از Git پاک شدن")
    safe_print("")
    safe_print("  📌 قدم بعدی:")
    safe_print("     git push origin main")
    safe_print("")
    safe_print("  ⚠️ اگه خطا داد:")
    safe_print("     - لینک GitHub رو Allow کن")
    safe_print("     - یا توکن‌ها رو Revoke کن")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
