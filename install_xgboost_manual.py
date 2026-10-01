# install_xgboost_manual.py
# نصب دستی xgboost
# اجرا: python install_xgboost_manual.py

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
    safe_print("  📦 نصب دستی xgboost")
    safe_print("=" * 80)
    safe_print("")

    # ۱. ارتقای pip
    safe_print("  🔧 ارتقای pip...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 0:
        safe_print("     ✅ pip ارتقا یافت")
    else:
        safe_print("     ⚠️ pip ارتقا نیافت")
    safe_print("")

    # ۲. نصب xgboost
    safe_print("  📦 نصب xgboost...")
    safe_print("     (ممکنه چند دقیقه طول بکشه)")
    safe_print("")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "xgboost"],
        capture_output=True,
        text=True,
        timeout=600,
    )

    safe_print(f"     Return code: {result.returncode}")
    safe_print("")

    if result.stdout:
        safe_print("  📤 stdout (آخرین خطوط):")
        for line in result.stdout.split("\\n")[-15:]:
            if line.strip():
                safe_print(f"     {line}")
        safe_print("")

    if result.stderr:
        safe_print("  ⚠️ stderr (آخرین خطوط):")
        for line in result.stderr.split("\\n")[-15:]:
            if line.strip():
                safe_print(f"     {line}")
        safe_print("")

    # ۳. تست
    safe_print("  🧪 تست نصب...")
    try:
        import importlib
        import xgboost
        importlib.reload(xgboost)
        safe_print(f"     ✅ xgboost v{xgboost.__version__}")
    except ImportError:
        safe_print("     ❌ xgboost نصب نشد")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
