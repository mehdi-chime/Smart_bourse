# remove_from_history.py
# پاک کردن توکن‌ها از تاریخچه‌ی Git
# اجرا: python remove_from_history.py

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
    return subprocess.run(
        ["git"] + args,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔒 پاک کردن از تاریخچه‌ی Git")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بکاپ
    safe_print("  📦 بکاپ...")
    backup_dir = PROJECT_ROOT / "backup" / "git_history"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"git_log_{timestamp}.txt"

    result = run_git(["log", "--oneline", "-20"])
    backup_file.write_text(result.stdout, encoding="utf-8")
    safe_print(f"     ✅ {backup_file.name}")
    safe_print("")

    # ۲. ببین آخرین commitها
    safe_print("  📋 آخرین ۱۰ commit:")
    safe_print("")

    result = run_git(["log", "--oneline", "-10"])
    for line in result.stdout.strip().split("\n"):
        safe_print(f"     {line}")

    safe_print("")

    # ۳. پاک کردن commit a3fefe8 از تاریخچه
    safe_print("  🗑️ پاک کردن commit a3fefe8 از تاریخچه...")
    safe_print("")

    # گزینه ۱: reset soft به commit قبل از a3fefe8
    result = run_git(["log", "--oneline", "-30"])
    commits = result.stdout.strip().split("\n")

    # پیدا کردن commit a3fefe8
    target_commit = "a3fefe8"
    commit_index = None

    for i, line in enumerate(commits):
        if line.startswith(target_commit):
            commit_index = i
            break

    if commit_index is None:
        safe_print("     ❌ commit a3fefe8 پیدا نشد!")
        safe_print("     شاید پاک شده.")
        return

    safe_print(f"     📌 commit {target_commit} در موقعیت {commit_index}")

    if commit_index + 1 < len(commits):
        parent_commit = commits[commit_index + 1].split()[0]
        safe_print(f"     📌 commit قبلی: {parent_commit}")
    else:
        safe_print("     ❌ commit قبلی پیدا نشد!")
        return

    safe_print("")

    # ۴. reset به parent
    safe_print(f"  🔄 Reset به {parent_commit}...")

    result = run_git(["reset", "--soft", parent_commit])

    if result.returncode == 0:
        safe_print(f"     ✅ Reset شد")
    else:
        safe_print(f"     ❌ خطا: {result.stderr}")

    safe_print("")

    # ۵. چک وضعیت
    safe_print("  📊 وضعیت:")
    safe_print("")

    result = run_git(["status", "--short"])
    for line in result.stdout.strip().split("\n")[:20]:
        if line:
            safe_print(f"     {line}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  📌 قدم بعدی:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  اگه می‌خوای همه تغییرات رو لغو کنی:")
    safe_print("     git reset --hard")
    safe_print("")
    safe_print("  یا اگه می‌خوای commit جدید بزنی:")
    safe_print("     git add .")
    safe_print("     git commit -m 'Clean history'")
    safe_print("     git push origin main --force")
    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()
