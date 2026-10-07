# install_scanner_ratio_filter.py
# اضافه کردن فیلتر ratio < 2 به اسکنر
# اجرا: python install_scanner_ratio_filter.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
AI_DIR = PROJECT_ROOT / "ai"
DATA_AI = PROJECT_ROOT / "data" / "ai"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  🔧 اضافه کردن فیلتر ratio < 2 به اسکنر")
    safe_print("=" * 70)
    safe_print("")

    # ===== قدم ۱: چک لیست‌ها =====
    safe_print("📁 قدم ۱: چک فایل‌های لیست...")

    good_file = DATA_AI / "good_symbols_v2.json"
    bad_file = DATA_AI / "bad_symbols_v2.json"

    good_symbols = []
    bad_symbols = []

    if good_file.exists():
        with open(good_file, "r", encoding="utf-8") as f:
            good_symbols = json.load(f)
        safe_print(f"   ✅ good_symbols_v2.json ({len(good_symbols)} سهم)")
    else:
        safe_print(f"   ⚠️  good_symbols_v2.json پیدا نشد")

    if bad_file.exists():
        with open(bad_file, "r", encoding="utf-8") as f:
            bad_symbols = json.load(f)
        safe_print(f"   ✅ bad_symbols_v2.json ({len(bad_symbols)} سهم)")
    else:
        safe_print(f"   ⚠️  bad_symbols_v2.json پیدا نشد")

    safe_print("")

    # ===== قدم ۲: ساخت ماژول فیلتر =====
    safe_print("📝 قدم ۲: ساخت ai/ratio_filter.py...")

    filter_content = '''# ai/ratio_filter.py
# فیلتر ratio < 2 + لیست سهم‌های خوب/بد
# اضافه شده به smart_scanner_v8

import json
from pathlib import Path

PROJECT_ROOT = Path(r"F:\\python\\har roz ba python\\smart_bours")
DATA_AI = PROJECT_ROOT / "data" / "ai"


class RatioFilter:
    """فیلتر ratio + سهم‌های خوب/بد"""

    def __init__(self):
        self.good_symbols = self._load("good_symbols_v2.json")
        self.bad_symbols = self._load("bad_symbols_v2.json")

    def _load(self, filename):
        f = DATA_AI / filename
        if not f.exists():
            return []
        try:
            with open(f, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except:
            return []

    def get_good_names(self):
        """اسم سهم‌های خوب"""
        return [s.get("symbol", "") for s in self.good_symbols]

    def get_bad_names(self):
        """اسم سهم‌های بد"""
        return [s.get("symbol", "") for s in self.bad_symbols]

    def is_bad(self, symbol):
        """چک کن سهم بد هست یا نه"""
        return symbol in self.get_bad_names()

    def is_good(self, symbol):
        """چک کن سهم خوب هست یا نه"""
        return symbol in self.get_good_names()

    def check_ratio(self, ratio):
        """چک کن ratio < 2 هست"""
        try:
            return float(ratio) < 2.0
        except:
            return True  # اگه نامشخص بود، رد نکن

    def apply(self, symbol, ratio):
        """
        اعمال فیلتر

        Returns:
            dict: {
                "pass": آیا رد بشه یا نه,
                "score_bonus": امتیاز اضافه,
                "reason": دلیل
            }
        """
        # ۱. چک سهم بد
        if self.is_bad(symbol):
            return {
                "pass": False,
                "score_bonus": 0,
                "reason": "سهم در لیست بد (Win Rate 0%)"
            }

        # ۲. چک ratio
        if not self.check_ratio(ratio):
            return {
                "pass": False,
                "score_bonus": 0,
                "reason": f"ratio={ratio} >= 2 (Win Rate 0%)"
            }

        # ۳. چک سهم خوب (امتیاز اضافه)
        bonus = 0
        reason = ""
        if self.is_good(symbol):
            bonus = 10
            reason = "سهم در لیست خوب (+10)"

        return {
            "pass": True,
            "score_bonus": bonus,
            "reason": reason
        }


# ===== تست =====
if __name__ == "__main__":
    f = RatioFilter()
    print(f"✅ لیست خوب: {len(f.get_good_names())} سهم")
    print(f"✅ لیست بد: {len(f.get_bad_names())} سهم")
    print()

    # تست
    tests = [
        ("دشیمی", 1.5),
        ("رتاپ", 1.5),   # توی لیست بده
        ("مداران", 1.5), # توی لیست بده
        ("XXX", 3.5),    # ratio بالا
    ]

    for sym, ratio in tests:
        result = f.apply(sym, ratio)
        status = "✅ قبول" if result["pass"] else "❌ رد"
        print(f"  {sym} (ratio={ratio}): {status}")
        if result["reason"]:
            print(f"     → {result['reason']}")
'''

    filter_file = AI_DIR / "ratio_filter.py"
    filter_file.write_text(filter_content, encoding="utf-8")
    safe_print(f"   ✅ ساخته شد: {filter_file}")
    safe_print("")

    # ===== قدم ۳: تست =====
    safe_print("=" * 70)
    safe_print("  🎯 قدم ۳: تست فیلتر")
    safe_print("=" * 70)
    safe_print("")

    os.chdir(AI_DIR)
    os.system(f"{sys.executable} ratio_filter.py")

    safe_print("")
    safe_print("=" * 70)
    safe_print("  🎉 نصب کامل شد!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📋 قدم بعدی:")
    safe_print("   - نتیجه رو بفرست")
    safe_print("   - بعدش فیلتر رو به smart_scanner_v8 اضافه می‌کنیم")
    safe_print("")


if __name__ == "__main__":
    main()
