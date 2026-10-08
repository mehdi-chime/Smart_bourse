# install_openai_ir.py
# نصب openai از mirror های ایرانی
# اجرا: python install_openai_ir.py

import os
import sys
import subprocess
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


# لیست mirror ها (به ترتیب اولویت)
MIRRORS = [
    # ۱. Runflare (ایرانی)
    ("Runflare (ایران)", "https://mirror-pypi.runflare.com/simple/", "mirror-pypi.runflare.com"),
    # ۲. Tsinghua (چین - معمولاً کار می‌کنه)
    ("Tsinghua (چین)", "https://pypi.tuna.tsinghua.edu.cn/simple/", "pypi.tuna.tsinghua.edu.cn"),
    # ۳. Aliyun (چین)
    ("Aliyun (چین)", "https://mirrors.aliyun.com/pypi/simple/", "mirrors.aliyun.com"),
    # ۴. Douban (چین)
    ("Douban (چین)", "https://pypi.doubanio.com/simple/", "pypi.doubanio.com"),
    # ۵. اصلی (اگه فیلترشکن داری)
    ("PyPI اصلی", "https://pypi.org/simple/", "pypi.org"),
]


def test_mirror(name, url, host):
    """تست یه mirror"""
    safe_print(f"\n{'=' * 70}")
    safe_print(f"  🔍 تست: {name}")
    safe_print(f"  📡 {url}")
    safe_print(f"{'=' * 70}\n")

    cmd = [
        sys.executable, "-m", "pip", "install",
        "openai", "httpx",
        "--index-url", url,
        "--trusted-host", host,
        "--timeout", "60",
        "--retries", "2",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=False,  # نشون بده
            timeout=300,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        safe_print(f"\n   ❌ Timeout ({name})\n")
        return False
    except Exception as e:
        safe_print(f"\n   ❌ خطا: {e}\n")
        return False


def check_installed():
    """چک نصب"""
    safe_print("\n" + "=" * 70)
    safe_print("  🧪 تست نصب")
    safe_print("=" * 70 + "\n")

    try:
        import openai
        safe_print(f"   ✅ openai: v{openai.__version__}")
    except ImportError:
        safe_print("   ❌ openai نصب نیست!")
        return False

    try:
        import httpx
        safe_print(f"   ✅ httpx: v{httpx.__version__}")
    except ImportError:
        safe_print("   ❌ httpx نصب نیست!")
        return False

    return True


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  📦 نصب openai از mirror های ایرانی")
    safe_print("=" * 70)

    # ===== اول چک کن نصب شده یا نه =====
    if check_installed():
        safe_print("\n✅ همه‌چیز نصبه! نیازی به نصب نیست.\n")
        input("Enter برای خروج...")
        return

    safe_print("\n⚠️  openai نصب نیست. شروع نصب...\n")

    # ===== تست هر mirror =====
    success = False
    for name, url, host in MIRRORS:
        try:
            if test_mirror(name, url, host):
                safe_print(f"\n✅ موفق با {name}!\n")
                success = True
                break
            else:
                safe_print(f"\n⚠️  {name} کار نکرد. می‌رم بعدی...\n")
        except KeyboardInterrupt:
            safe_print("\n❌ لغو شد.\n")
            return

    # ===== چک نهایی =====
    if success:
        if check_installed():
            safe_print("\n" + "=" * 70)
            safe_print("  🎉 نصب کامل شد!")
            safe_print("=" * 70)
            safe_print("")
            safe_print("📋 قدم بعدی:")
            safe_print("   python ai\\llm_analyzer.py")
            safe_print("")
        else:
            safe_print("\n❌ متأسفانه نصب تأیید نشد.\n")
    else:
        safe_print("\n" + "=" * 70)
        safe_print("  ❌ همه‌ی mirror ها fail شدن!")
        safe_print("=" * 70)
        safe_print("")
        safe_print("📋 راه‌حل‌ها:")
        safe_print("   ۱. فیلترشکن روشن کن")
        safe_print("   ۲. اینترنت عوض کن")
        safe_print("   ۳. بعداً امتحان کن")
        safe_print("")

    input("Enter برای خروج...")


if __name__ == "__main__":
    main()
