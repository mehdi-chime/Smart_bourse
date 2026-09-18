"""
Project : Smart_Bourse
File    : auto_push.py
Version : 2.0.0
Author  : Mehdi Jalali + Assistant

Description :
    آپلود خودکار همه‌ی تغییرات به گیت‌هاب
    - تشخیص فایل‌های تغییر یافته
    - کامیت هوشمند
    - پوش خودکار
    - مدیریت خطا
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).parent.resolve()


# ======================================================================
# ابزار اجرای دستور
# ======================================================================

def run(cmd, cwd=None):
    """اجرای دستور شل"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


# ======================================================================
# بررسی‌ها
# ======================================================================

def check_git():
    """چک کن گیت نصبه"""
    code, out, err = run("git --version")
    if code != 0:
        print("❌ گیت نصب نیست!")
        print("   دانلود: https://git-scm.com/download/win")
        return False
    print("✅ " + out)
    return True


def check_repo():
    """چک کن مخزن گیت هست"""
    code, out, err = run("git rev-parse --is-inside-work-tree")
    if code != 0 or out.strip() != "true":
        print("❌ این پوشه مخزن گیت نیست!")
        print("   اول این رو بزن: git init")
        return False
    print("✅ مخزن گیت شناسایی شد")
    return True


def check_remote():
    """چک کن ریموت تنظیم شده"""
    code, out, err = run("git remote -v")
    if "origin" not in out:
        print("⚠️  ریموت origin تنظیم نیست")
        print("   اجرا کن:")
        print('   git remote add origin https://github.com/mehdi-chime/Smart_bourse.git')
        return False
    print("✅ ریموت origin تنظیم است")
    return True


# ======================================================================
# وضعیت
# ======================================================================

def show_status():
    """نمایش وضعیت"""
    code, out, err = run("git status --short")
    if not out:
        print()
        print("ℹ️  هیچ تغییری نیست. همه‌چیز آپدیت است.")
        return False

    print()
    print("📋 فایل‌های تغییر یافته:")
    lines = out.split("\n")
    for line in lines[:30]:
        print("   " + line)
    if len(lines) > 30:
        print("   ... و " + str(len(lines) - 30) + " فایل دیگه")
    print()
    print("   مجموع: " + str(len(lines)) + " فایل")
    return True


# ======================================================================
# آپلود
# ======================================================================

def stage_all():
    """اضافه کردن همه‌چیز"""
    print()
    print("📦 اضافه کردن فایل‌ها ...")
    code, out, err = run("git add -A")
    if code != 0:
        print("❌ خطا: " + err)
        return False
    print("✅ فایل‌ها اضافه شدند")
    return True


def commit():
    """کامیت با پیام هوشمند"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = "Auto-update: " + timestamp

    print()
    print("💾 کامیت ...")
    code, out, err = run('git commit -m "' + msg + '"')

    if code != 0:
        if "nothing to commit" in (out + err):
            print("ℹ️  چیزی برای کامیت نیست")
            return False
        print("❌ خطا در کامیت:")
        print(err)
        return False

    print("✅ کامیت شد: " + msg)
    return True


def get_branch():
    """شاخه فعلی"""
    code, out, err = run("git rev-parse --abbrev-ref HEAD")
    if code != 0:
        return "main"
    return out.strip() or "main"


def push():
    """پوش به گیت‌هاب"""
    branch = get_branch()

    print()
    print("🚀 پوش به origin/" + branch + " ...")
    code, out, err = run("git push origin " + branch)

    if code != 0:
        print("❌ خطا در پوش:")
        print(err)
        print()
        print("راهنما:")
        print("  - اگه خطای authentication دادی، این رو بزن:")
        print("    git config --global credential.helper store")
        print("  - بعد دوباره auto_push.py رو اجرا کن")
        return False

    print("✅ پوش موفق")
    if out:
        print(out)
    return True


# ======================================================================
# اجرای اصلی
# ======================================================================

def main():
    print()
    print("=" * 60)
    print("  🚀 Smart_Bourse Auto Push")
    print("=" * 60)
    print("  مسیر پروژه: " + str(ROOT))
    print()

    # ۱. بررسی‌ها
    if not check_git():
        return
    if not check_repo():
        return
    if not check_remote():
        return

    # ۲. وضعیت
    if not show_status():
        return

    # ۳. تایید
    print()
    ans = input("➡️  آپلود به گیت‌هاب؟ (y/n): ").strip().lower()
    if ans != "y":
        print("لغو شد.")
        return

    # ۴. آپلود
    if not stage_all():
        return
    if not commit():
        return
    if not push():
        return

    # ۵. لینک
    code, url, err = run("git remote get-url origin")
    if url:
        url = url.strip().replace(".git", "")
        branch = get_branch()
        print()
        print("🔗 لینک:")
        print("   " + url + "/tree/" + branch)

    print()
    print("=" * 60)
    print("  ✅ تمام! همه‌چیز روی گیت‌هاب آپدیت شد.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()