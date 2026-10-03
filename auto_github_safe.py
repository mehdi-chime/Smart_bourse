# auto_github_safe.py
# آپلود امن به GitHub — بدون توکن
# اجرا: python auto_github_safe.py

import os
import sys
import subprocess
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


def run_git(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="ignore",
        )
        return result
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        return None


def check_git_repo():
    safe_print("  🔍 چک Git repo...")
    result = run_git(["status"])
    if result and result.returncode == 0:
        safe_print("     ✅ Git repo")
        return True
    else:
        safe_print("     ❌ Git repo نیست!")
        return False


def check_secrets():
    """چک امنیت — توکن نره GitHub"""
    safe_print("  🔒 چک امنیت...")

    # ۱. چک فایل alert_config.py
    alert_file = PROJECT_ROOT / "scanner" / "alert_config.py"
    if alert_file.exists():
        content = alert_file.read_text(encoding="utf-8")
        if "bot502704" in content or "b4916751" in content:
            safe_print("     ⚠️ توکن واقعی در alert_config.py هست")
            safe_print("     ✅ ولی توی .gitignore هست")

    # ۲. چک .gitignore
    gitignore = PROJECT_ROOT / ".gitignore"
    if not gitignore.exists():
        safe_print("     ❌ .gitignore نیست!")
        return False

    content = gitignore.read_text(encoding="utf-8")
    if "alert_config.py" not in content:
        safe_print("     ❌ alert_config.py در .gitignore نیست!")
        return False

    safe_print("     ✅ .gitignore درسته")

    # ۳. چک git status
    result = run_git(["status", "--porcelain"])
    if result:
        lines = result.stdout.split("\n")
        for line in lines:
            if "alert_config" in line and "example" not in line:
                safe_print(f"     🚨 خطر! {line}")
                return False

    safe_print("     ✅ alert_config.py در git status نیست")
    return True


def git_add():
    safe_print("  📦 git add . ...")
    result = run_git(["add", "."])
    if result and result.returncode == 0:
        safe_print("     ✅ اضافه شد")
        return True
    else:
        safe_print("     ❌ خطا")
        return False


def check_staged():
    """چک فایل‌های staged"""
    safe_print("  🔍 چک فایل‌های staged...")

    result = run_git(["diff", "--cached", "--name-only"])
    if not result or result.returncode != 0:
        return True

    files = result.stdout.strip().split("\n")

    # چک alert_config
    for f in files:
        if "alert_config" in f and "example" not in f:
            safe_print(f"     🚨 خطر! {f} در staged هست!")
            safe_print(f"     🚨 این فایل توکن داره! حذفش کن!")
            return False

    safe_print(f"     ✅ {len(files)} فایل staged (امن)")

    # نمایش چند فایل
    important = [f for f in files if f.endswith(".py")][:5]
    for f in important:
        safe_print(f"        - {f}")

    return True


def git_commit():
    safe_print("  💾 git commit...")

    commit_msg = f"v9 — School Mode with AI ({datetime.now().strftime('%Y-%m-%d')})"

    result = run_git(["commit", "-m", commit_msg])
    if result:
        if result.returncode == 0:
            safe_print("     ✅ Commit شد")
            return True
        else:
            if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                safe_print("     ℹ️ چیزی برای commit نیست")
                return True
            safe_print(f"     ⚠️ {result.stdout[:200]}")
            return False
    return False


def git_push():
    safe_print("  🚀 git push...")

    result = run_git(["push", "origin", "main"])
    if result:
        if result.returncode == 0:
            safe_print("     ✅ Push شد")
            return True
        else:
            safe_print(f"     ❌ خطا:")
            if result.stderr:
                for line in result.stderr.split("\n")[:5]:
                    if line.strip():
                        safe_print(f"        {line}")
            return False
    return False


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 آپلود امن به GitHub")
    safe_print("=" * 80)
    safe_print("")

    # ۱. Git repo
    if not check_git_repo():
        return
    safe_print("")

    # ۲. امنیت
    if not check_secrets():
        safe_print("")
        safe_print("  🚨 آپلود متوقف شد!")
        safe_print("  دلیل: مشکل امنیتی")
        safe_print("")
        safe_print("=" * 80)
        return
    safe_print("")

    # ۳. git add
    if not git_add():
        return
    safe_print("")

    # ۴. چک staged
    if not check_staged():
        safe_print("")
        safe_print("  🚨 آپلود متوقف شد!")
        safe_print("  دلیل: فایل حساس در staged")
        safe_print("")
        safe_print("=" * 80)
        return
    safe_print("")

    # ۵. git commit
    if not git_commit():
        return
    safe_print("")

    # ۶. git push
    if not git_push():
        return
    safe_print("")

    # ۷. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ Git repo چک شد")
    safe_print("  ✅ امنیت چک شد")
    safe_print("  ✅ alert_config.py محافظت شده")
    safe_print("  ✅ Commit انجام شد")
    safe_print("  ✅ Push انجام شد")
    safe_print("")
    safe_print("  🎉 آپلود موفق!")
    safe_print("")
    safe_print("  ⚠️ نکته: توکن ایتا در GitHub نرفت!")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
