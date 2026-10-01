# sync_for_ai.py
"""
اسکریپت آماده‌سازی و آپلود فایل‌های کلیدی پروژه به گیت‌هاب
تا دستیار هوش مصنوعی بتواند از راه دور به آن‌ها دسترسی داشته باشد.
"""

import os
import subprocess
import sys
from datetime import datetime

# ---- فایل‌ها/پوشه‌هایی که می‌خواهیم در گیت‌هاب موجود باشند ----
KEY_FILES = [
    # ساختار و تنظیمات
    "config.py",
    "project_config.py",
    "requirements.txt",
    "README.md",
    "main.py",
    "run.py",

    # دیتای بازار
    "market.py",
    "market_manager.py",
    "market_downloader.py",

    # فیلترها و اسکنر
    "filter_volume.py",
    "scanner/__init__.py",
    "scanner/*.py",

    # دیتابیس
    "database/__init__.py",
    "database/*.py",

    # ماژول‌های تحلیلی
    "analysis/__init__.py",
    "analysis/*.py",
    "indicators/__init__.py",
    "indicators/*.py",
    "strategy/__init__.py",
    "strategy/*.py",

    # پوشه‌های گزارش/داده (فقط اسکریپت‌ها، نه دیتای سنگین)
    "reports/*.py",
    "reports/*.md",
    "utils/__init__.py",
    "utils/*.py",

    # چک‌های سلامت
    "check_data.py",
    "test_database.py",

    # RoadMap‌ها
    "Smart_Bourse_RoadMap.txt",
    "DeepSeek_RoadMap.txt",
]

# ---- پسوندهایی که نباید آپلود شوند (دیتای سنگین) ----
EXCLUDE_EXT = {".csv", ".xlsx", ".db", ".sqlite", ".parquet", ".log", ".pkl", ".h5"}


def run(cmd, cwd=None):
    """اجرای دستور شل و برگرداندن خروجی"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, encoding="utf-8"
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def check_git_repo():
    code, out, err = run("git rev-parse --is-inside-work-tree")
    if code != 0 or out.strip() != "true":
        print("❌ این پوشه یک مخزن گیت نیست. اول دستور `git init` را اجرا کن.")
        sys.exit(1)
    print("✅ مخزن گیت شناسایی شد.")


def check_remote():
    code, out, err = run("git remote -v")
    if "origin" not in out:
        print("⚠️  ریموت origin تنظیم نشده است.")
        print("   اجرا کن: git remote add origin https://github.com/mehdi-chime/Smart_bourse.git")
        sys.exit(1)
    print("✅ ریموت origin تنظیم است.")


def show_status():
    code, out, err = run("git status --short")
    print("\n📋 وضعیت فعلی گیت:")
    if out:
        print(out)
    else:
        print("   (پاک است، تغییری نیست)")


def stage_key_files():
    """فایل‌های کلیدی را stage می‌کند"""
    print("\n📦 اضافه کردن فایل‌های کلیدی به git ...")
    added = []
    skipped = []

    # اول همه تغییرات فعلی را اضافه کن
    run("git add -A")

    # بعد فایل‌های سنگین را از stage خارج کن
    for root, dirs, files in os.walk("."):
        # پوشه‌های مخفی و مجازی را رد کن
        dirs[:] = [d for d in dirs if d not in
                   {".git", "__pycache__", ".venv", "venv", "env",
                    "node_modules", ".idea", ".vscode"}]

        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXCLUDE_EXT:
                path = os.path.join(root, f)
                code, _, _ = run(f'git reset HEAD "{path}"')
                if code == 0:
                    skipped.append(path)

    if skipped:
        print(f"   🚫 {len(skipped)} فایل سنگین از stage خارج شد.")
    print("   ✅ فایل‌های سبک stage شدند.")


def commit_and_push():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    msg = f"Sync for AI review - {timestamp}"

    code, out, err = run(f'git commit -m "{msg}"')
    if code != 0:
        if "nothing to commit" in (out + err):
            print("\nℹ️  چیزی برای commit نیست — همه چیز قبلاً آپلود شده.")
        else:
            print(f"\n❌ خطا در commit:\n{err}")
            return
    else:
        print(f"\n✅ Commit ساخته شد: {msg}")

    # تشخیص نام برنچ فعلی
    _, branch, _ = run("git rev-parse --abbrev-ref HEAD")
    branch = branch.strip() or "main"

    print(f"🚀 Push به origin/{branch} ...")
    code, out, err = run(f"git push origin {branch}")
    if code != 0:
        print(f"❌ خطا در push:\n{err}")
        print("\nراهنما:")
        print("  - اگر خطای authentication دادی: git config --global credential.helper store")
        print("  - اگر برنچ متفاوت است: git push -u origin main")
    else:
        print(f"✅ با موفقیت push شد: {out}")


def print_branch_url():
    """لینک گیت‌هاب برنچ را چاپ می‌کند"""
    _, url, _ = run("git remote get-url origin")
    if url:
        url = url.strip().replace(".git", "")
        _, branch, _ = run("git rev-parse --abbrev-ref HEAD")
        branch = branch.strip() or "main"
        print(f"\n🔗 لینک برای دستیار AI:\n   {url}/tree/{branch}")


def main():
    print("=" * 55)
    print("   Smart_Bourse — Sync for AI")
    print("=" * 55)

    check_git_repo()
    check_remote()
    show_status()

    ans = input("\n➡️  فایل‌های کلیدی stage شوند و push شود؟ (y/n): ").strip().lower()
    if ans != "y":
        print("لغو شد.")
        return

    stage_key_files()
    commit_and_push()
    print_branch_url()

    print("\n🎉 تمام. حالا لینک بالا را به دستیار AI بده.")


if __name__ == "__main__":
    main()
