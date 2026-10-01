
from pathlib import Path
import subprocess
import sys


# ============================================================
# Smart Bourse
# انتقال فایل‌های Python موجود در کامپیوتر ولی غایب در GitHub
# ============================================================

PROJECT_PATH = Path(__file__).resolve().parent


def run_git(*args):
    """اجرای دستور Git و برگرداندن خروجی"""
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_PATH,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        print("\n❌ خطا در اجرای Git:")
        print(result.stderr)
        return None

    return result.stdout.strip()


def main():
    print("=" * 70)
    print("   Smart Bourse - GitHub Python Sync")
    print("=" * 70)

    print(f"\n📁 مسیر پروژه:")
    print(PROJECT_PATH)

    # --------------------------------------------------------
    # 1. بررسی Git
    # --------------------------------------------------------
    print("\n🔄 دریافت آخرین وضعیت GitHub...")

    fetch_result = run_git("fetch", "origin")

    if fetch_result is None:
        print("\n❌ نتوانستم اطلاعات GitHub را دریافت کنم.")
        input("\nEnter را بزنید...")
        return

    # --------------------------------------------------------
    # 2. پیدا کردن فایل‌های Python موجود روی GitHub
    # --------------------------------------------------------
    print("\n🔍 بررسی فایل‌های Python موجود در GitHub...")

    remote_files_output = run_git(
        "ls-tree",
        "-r",
        "--name-only",
        "origin/main"
    )

    if remote_files_output is None:
        print("\n❌ نتوانستم فایل‌های GitHub را بررسی کنم.")
        input("\nEnter را بزنید...")
        return

    remote_files = set(
        line.strip()
        for line in remote_files_output.splitlines()
        if line.strip()
    )

    # فقط فایل‌های .py روی GitHub
    remote_python_files = {
        f for f in remote_files
        if f.lower().endswith(".py")
    }

    # --------------------------------------------------------
    # 3. پیدا کردن تمام فایل‌های Python روی کامپیوتر
    # --------------------------------------------------------
    print("🔍 پیدا کردن فایل‌های Python داخل Smart_Bourse...")

    local_python_files = []

    for path in PROJECT_PATH.rglob("*.py"):

        # فایل‌های داخل .git را نادیده بگیر
        if ".git" in path.parts:
            continue

        # __pycache__ را نادیده بگیر
        if "__pycache__" in path.parts:
            continue

        relative_path = path.relative_to(PROJECT_PATH).as_posix()
        local_python_files.append(relative_path)

    local_python_files = set(local_python_files)

    # --------------------------------------------------------
    # 4. مقایسه
    # --------------------------------------------------------
    missing_files = sorted(
        local_python_files - remote_python_files
    )

    print("\n" + "=" * 70)
    print("نتیجه مقایسه")
    print("=" * 70)

    print(f"\n🐍 فایل‌های Python روی کامپیوتر: {len(local_python_files)}")
    print(f"🐙 فایل‌های Python روی GitHub:    {len(remote_python_files)}")
    print(f"📤 فایل‌های Python غایب از GitHub: {len(missing_files)}")

    # --------------------------------------------------------
    # 5. اگر چیزی پیدا نشد
    # --------------------------------------------------------
    if not missing_files:
        print("\n✅ هیچ فایل Python جدیدی برای انتقال وجود ندارد.")
        print("GitHub از نظر فایل‌های Python با پروژه محلی هماهنگ است.")

        input("\nEnter را بزنید...")
        return

    # --------------------------------------------------------
    # 6. نمایش فایل‌هایی که قرار است منتقل شوند
    # --------------------------------------------------------
    print("\n📋 فایل‌هایی که قرار است به GitHub اضافه شوند:\n")

    for i, file in enumerate(missing_files, 1):
        print(f"{i:3}. {file}")

    # --------------------------------------------------------
    # 7. تأیید کاربر
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("⚠️ فقط فایل‌های Python که در GitHub نیستند اضافه خواهند شد.")
    print("⚠️ فایل‌های JSON، DB، LOG، PYD و __pycache__ منتقل نمی‌شوند.")
    print("=" * 70)

    answer = input("\nآیا این فایل‌ها به GitHub منتقل شوند؟ (y/n): ")

    if answer.lower() not in ("y", "yes"):
        print("\n❌ عملیات لغو شد.")
        input("\nEnter را بزنید...")
        return

    # --------------------------------------------------------
    # 8. اضافه کردن فایل‌ها به Git
    # --------------------------------------------------------
    print("\n📦 اضافه کردن فایل‌ها به Git...")

    for file in missing_files:
        result = run_git("add", "--", file)

        if result is None:
            print(f"❌ خطا در اضافه کردن: {file}")
            input("\nEnter را بزنید...")
            return

        print(f"✅ اضافه شد: {file}")

    # --------------------------------------------------------
    # 9. Commit
    # --------------------------------------------------------
    print("\n💾 ساخت Commit...")

    commit_message = (
        f"Add missing Python files ({len(missing_files)} files)"
    )

    commit_result = run_git(
        "commit",
        "-m",
        commit_message
    )

    if commit_result is None:
        print("\n❌ Commit انجام نشد.")
        input("\nEnter را بزنید...")
        return

    print("\n✅ Commit با موفقیت انجام شد.")
    print(commit_result)

    # --------------------------------------------------------
    # 10. Push
    # --------------------------------------------------------
    print("\n🚀 ارسال فایل‌ها به GitHub...")

    push_result = run_git(
        "push",
        "origin",
        "main"
    )

    if push_result is None:
        print("\n❌ Push انجام نشد.")
        print("ممکن است مشکل اتصال یا احراز هویت GitHub وجود داشته باشد.")
        input("\nEnter را بزنید...")
        return

    print("\n" + "=" * 70)
    print("🎉 عملیات با موفقیت کامل شد!")
    print("=" * 70)

    print("\nفایل‌های Python جدید اکنون روی GitHub قرار دارند.")

    print("\n📌 فایل‌های منتقل‌شده:")

    for file in missing_files:
        print(f"   ✅ {file}")

    print("\n" + "=" * 70)

    input("\nEnter را بزنید...")


if __name__ == "__main__":
    main()

