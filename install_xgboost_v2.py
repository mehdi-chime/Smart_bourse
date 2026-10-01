# install_xgboost_v2.py
# نصب xgboost — تلاش نهایی
# اجرا: python install_xgboost_v2.py

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
    safe_print("  📦 نصب xgboost — تلاش نهایی")
    safe_print("=" * 80)
    safe_print("")

    # چک
    try:
        import xgboost
        safe_print(f"  ✅ xgboost v{xgboost.__version__}")
        return
    except ImportError:
        safe_print("  ⚠️ نصب نیست")
        safe_print("")

    # تلاش با تنظیمات خاص
    safe_print("  📦 تلاش با تنظیمات طولانی...")
    safe_print("     (ممکنه ۳۰ دقیقه طول بکشه)")
    safe_print("")

    cmd = [
        sys.executable, "-m", "pip", "install",
        "xgboost",
        "--timeout", "600",
        "--retries", "20",
        "--no-cache-dir",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=2400,  # 40 دقیقه
        )
        
        safe_print(f"     Return: {result.returncode}")
        safe_print("")
        
        if result.stdout:
            safe_print("  📤 stdout:")
            for line in result.stdout.split("\\n")[-10:]:
                if line.strip():
                    safe_print(f"     {line}")
            safe_print("")
        
        if result.stderr:
            safe_print("  ⚠️ stderr:")
            for line in result.stderr.split("\\n")[-10:]:
                if line.strip():
                    safe_print(f"     {line}")
            safe_print("")
    except Exception as e:
        safe_print(f"  ❌ {e}")
        safe_print("")

    # تست
    safe_print("  🧪 تست...")
    try:
        import xgboost
        safe_print(f"     ✅ xgboost v{xgboost.__version__}")
    except ImportError:
        safe_print("     ❌ نصب نشد")
        safe_print("")
        safe_print("  💡 پیشنهاد:")
        safe_print("     1. بریم فاز ۱۱ (بک‌تست)")
        safe_print("     2. بعداً xgboost رو نصب کن")
        safe_print("     3. RandomForest هم کافیه!")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
