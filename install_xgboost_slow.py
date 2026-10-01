# install_xgboost_slow.py
# نصب xgboost با timeout بیشتر
# اجرا: python install_xgboost_slow.py

import os
import sys
import subprocess

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


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📦 نصب xgboost با timeout بیشتر")
    safe_print("=" * 80)
    safe_print("")

    # تنظیم timeout بیشتر
    safe_print("  🔧 تنظیم timeout بیشتر...")
    safe_print("     (اینترنت کند هست، صبر می‌کنیم)")
    safe_print("")

    # نصب با تنظیمات
    safe_print("  📦 نصب xgboost...")
    safe_print("     این ممکنه ۵-۱۵ دقیقه طول بکشه!")
    safe_print("")

    cmd = [
        sys.executable, "-m", "pip", "install",
        "xgboost",
        "--timeout", "300",
        "--retries", "10",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=1800,  # 30 دقیقه
    )

    safe_print(f"     Return code: {result.returncode}")
    safe_print("")

    if result.stdout:
        safe_print("  📤 stdout:")
        for line in result.stdout.split("\\n")[-20:]:
            if line.strip():
                safe_print(f"     {line}")
        safe_print("")

    if result.stderr:
        safe_print("  ⚠️ stderr:")
        for line in result.stderr.split("\\n")[-20:]:
            if line.strip():
                safe_print(f"     {line}")
        safe_print("")

    # تست
    safe_print("  🧪 تست نصب...")
    try:
        import xgboost
        safe_print(f"     ✅ xgboost v{xgboost.__version__}")
    except ImportError:
        safe_print("     ❌ نصب نشد")
        safe_print("")
        safe_print("  💡 راه‌حل‌های دیگه:")
        safe_print("     1. از VPN استفاده کن")
        safe_print("     2. از mirror داخلی استفاده کن")
        safe_print("     3. دستی دانلود کن")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
