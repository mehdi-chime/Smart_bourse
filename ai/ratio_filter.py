# ai/ratio_filter.py
# فیلتر ratio < 2 + لیست سهم‌های خوب/بد
# اضافه شده به smart_scanner_v8

import json
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
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
