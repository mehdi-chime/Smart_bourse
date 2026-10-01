# install_sklearn.py
# نصب scikit-learn
# اجرا: python install_sklearn.py

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


def install_package(package):
    """نصب یه پکیج"""
    safe_print(f"  📦 نصب {package}...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        if result.returncode == 0:
            safe_print(f"     ✅ {package} نصب شد")
            return True
        else:
            safe_print(f"     ❌ خطا:")
            safe_print(result.stderr[:500])
            return False
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        return False


def check_package(package):
    """چک نصب بودن پکیج"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📦 نصب scikit-learn")
    safe_print("=" * 80)
    safe_print("")

    # چک
    safe_print("  🔍 چک پکیج‌ها...")
    
    packages = [
        ("sklearn", "scikit-learn"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    for import_name, pip_name in packages:
        if check_package(import_name):
            safe_print(f"     ✅ {pip_name} از قبل نصب")
        else:
            safe_print(f"     ⚠️ {pip_name} نصب نیست")
    safe_print("")

    # نصب
    safe_print("  📦 نصب پکیج‌های لازم...")
    safe_print("")

    to_install = [
        "scikit-learn",
        "numpy",
        "pandas",
    ]

    for package in to_install:
        install_package(package)
        safe_print("")

    # تست
    safe_print("  🧪 تست نهایی...")
    try:
        import sklearn
        import numpy
        import pandas
        safe_print(f"     ✅ scikit-learn v{sklearn.__version__}")
        safe_print(f"     ✅ numpy v{numpy.__version__}")
        safe_print(f"     ✅ pandas v{pandas.__version__}")
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")

    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
