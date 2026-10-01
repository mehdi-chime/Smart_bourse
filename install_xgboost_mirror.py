# install_xgboost_mirror.py
# نصب xgboost از mirror داخلی
# اجرا: python install_xgboost_mirror.py

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


MIRRORS = [
    ("Runflare", "https://mirror-pypi.runflare.com/simple/"),
    ("Tsinghua", "https://pypi.tuna.tsinghua.edu.cn/simple/"),
    ("Aliyun", "https://mirrors.aliyun.com/pypi/simple/"),
    ("Douban", "https://pypi.douban.com/simple/"),
]


def try_mirror(name, url):
    """تلاش با یه mirror"""
    safe_print(f"  🌐 تلاش با {name}...")
    safe_print(f"     {url}")
    
    cmd = [
        sys.executable, "-m", "pip", "install",
        "xgboost",
        "-i", url,
        "--trusted-host", url.split("/")[2],
        "--timeout", "300",
        "--retries", "5",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900,
        )
        
        if result.returncode == 0:
            safe_print(f"     ✅ نصب شد!")
            return True
        else:
            safe_print(f"     ❌ خطا")
            if result.stderr:
                for line in result.stderr.split("\\n")[-5:]:
                    if line.strip():
                        safe_print(f"        {line}")
            return False
    except Exception as e:
        safe_print(f"     ❌ {e}")
        return False


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📦 نصب xgboost از mirror")
    safe_print("=" * 80)
    safe_print("")

    # تست نصب فعلی
    try:
        import xgboost
        safe_print(f"  ✅ xgboost از قبل نصب است: v{xgboost.__version__}")
        return
    except ImportError:
        safe_print("  ⚠️ xgboost نصب نیست")
        safe_print("")

    # تلاش با mirrorها
    for name, url in MIRRORS:
        if try_mirror(name, url):
            # تست
            safe_print("")
            safe_print("  🧪 تست نهایی...")
            try:
                import importlib
                import xgboost
                importlib.reload(xgboost)
                safe_print(f"     ✅ xgboost v{xgboost.__version__}")
            except ImportError:
                safe_print("     ❌ خطا در تست")
            safe_print("")
            safe_print("=" * 80)
            safe_print("  ✅ تمام!")
            safe_print("=" * 80)
            safe_print("")
            return
        safe_print("")

    # اگه همه شکست خورد
    safe_print("  ❌ همه mirrorها شکست خوردند")
    safe_print("")
    safe_print("  💡 راه‌حل‌های دیگه:")
    safe_print("     1. از VPN استفاده کن")
    safe_print("     2. شب دوباره امتحان کن")
    safe_print("     3. بریم فاز ۱۱ (بک‌تست) و بعداً xgboost")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
